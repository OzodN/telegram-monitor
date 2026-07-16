from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

from src.aggregator import aggregate_report_data
from src.auditor import audit_classified_posts
from src.classifier import classify_posts
from src.classification_support import load_classification_reference_data
from src.config_loader import load_app_config
from src.gemini_client import GeminiClient
from src.narrative_generator import generate_narrative
from src.narrative_validator import validate_narrative
from src.regression_checks import run_regression_checks
from src.report_generator import generate_report_docx
from src.report_period import calculate_report_period
from src.telegram_fetcher import fetch_telegram_posts
from src.utils import configure_logging, ensure_run_directories, write_json


logger = logging.getLogger(__name__)


def main() -> None:
    root_dir = Path(__file__).resolve().parent
    load_dotenv(root_dir / ".env")
    configure_logging()

    config = load_app_config(root_dir / "config.yaml")

    # Prompt the user to select the report period interactively if running in a TTY terminal.
    # Falls back to the configured default mode if not in a TTY or if interrupted.
    if sys.stdin.isatty():
        print("\nHisobot davrini tanlang / Select report period:")
        print("1. Joriy hafta (Current week)")
        print("2. O'tgan hafta (Previous week)")
        while True:
            try:
                choice = input("Tanlovingiz / Choice [1-2]: ").strip()
                if choice == "1":
                    config.report_period.mode = "current_week"
                    break
                elif choice == "2":
                    config.report_period.mode = "previous_week"
                    break
                else:
                    print("Noto'g'ri tanlov. Iltimos, 1 yoki 2 ni kiriting. / Invalid choice. Please enter 1 or 2.")
            except (KeyboardInterrupt, EOFError):
                print(f"\nTerminal input interrupted. Falling back to configured mode: {config.report_period.mode}")
                break
    else:
        logger.info("Non-interactive session. Using configured report period mode: %s", config.report_period.mode)

    reference_data = load_classification_reference_data(config.paths)
    gemini_client = GeminiClient(config.gemini)
    run_dirs = ensure_run_directories(root_dir, config.paths.output_root)
    period = calculate_report_period(config.report_period, config.timezone)
    logger.info("Report period: %s - %s", period.start.isoformat(), period.end.isoformat())

    raw_posts = asyncio.run(fetch_telegram_posts(config.telegram, period))
    write_json(run_dirs.raw_posts_path, [post.to_dict() for post in raw_posts])

    classified_posts = classify_posts(raw_posts, config.gemini, config.paths, reference_data, gemini_client)
    write_json(run_dirs.classified_posts_path, [post.to_dict() for post in classified_posts])

    classification_regression_report = run_regression_checks(
        classified_posts,
        reference_data,
        stage_name="classification",
    )
    write_json(run_dirs.classification_regression_checks_path, classification_regression_report)

    audited_posts = audit_classified_posts(classified_posts, config.gemini, reference_data, gemini_client)
    write_json(run_dirs.audited_posts_path, [post.to_dict() for post in audited_posts])

    audited_regression_report = run_regression_checks(
        audited_posts,
        reference_data,
        stage_name="audit",
    )
    write_json(run_dirs.audit_regression_checks_path, audited_regression_report)

    aggregated = aggregate_report_data(
        classified_posts=audited_posts,
        channels=config.telegram.channels,
        period=period,
        reference_data=reference_data,
    )
    write_json(run_dirs.aggregated_stats_path, aggregated.to_dict())

    narrative = generate_narrative(audited_posts, aggregated, config.gemini, config.paths, gemini_client)
    narrative_validation_report = validate_narrative(narrative, aggregated, config.paths)
    write_json(run_dirs.narrative_path, narrative.to_dict())
    write_json(run_dirs.narrative_validation_path, narrative_validation_report)

    report_path = generate_report_docx(
        reference_report_path=config.paths.reference_report_docx,
        output_dir=run_dirs.reports_dir,
        aggregated=aggregated,
        narrative=narrative,
    )
    logger.info("Generated report: %s", report_path)

    print(f"""
======================================================================
███████╗██╗   ██╗ ██████╗ ██████╗ ███████╗███████╗███████╗
██╔════╝██║   ██║██╔════╝██╔════╝ ██╔════╝██╔════╝██╔════╝
███████╗██║   ██║██║     ██║      █████╗  ███████╗███████╗
╚════██║██║   ██║██║     ██║      ██╔══╝  ╚════██║╚════██║
███████║╚██████╔╝╚██████╗╚██████╗ ███████╗███████║███████║
╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝ ╚══════╝╚══════╝╚══════╝

🎉 ОТЧЕТ УСПЕШНО СГЕНЕРИРОВАН! 🎉
📁 Путь: {report_path}
======================================================================
""")


if __name__ == "__main__":
    main()
