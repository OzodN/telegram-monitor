from __future__ import annotations

import asyncio
import getpass
import logging
from pathlib import Path

import qrcode
from telethon import TelegramClient
from telethon.errors import PasswordHashInvalidError, SessionPasswordNeededError
from telethon.tl.functions.channels import GetFullChannelRequest

from src.models import ReportPeriod, TelegramConfig, TelegramPost


logger = logging.getLogger(__name__)


async def fetch_telegram_posts(config: TelegramConfig, period: ReportPeriod) -> list[TelegramPost]:
    posts: list[TelegramPost] = []
    client = TelegramClient(config.session_name, config.api_id, config.api_hash)

    await client.connect()
    try:
        await _ensure_authorized(client, config.session_name)

        for channel in config.channels:
            try:
                entity = await client.get_entity(channel.telegram_url)
                subscriber_count = await _load_subscriber_count(client, entity)
                channel_posts = await _fetch_channel_posts(
                    client=client,
                    entity=entity,
                    council_name=channel.council_name,
                    channel_url=channel.telegram_url,
                    subscriber_count=subscriber_count,
                    period=period,
                )
                posts.extend(channel_posts)
                logger.info(
                    "Fetched %s posts from %s",
                    len(channel_posts),
                    channel.council_name,
                )
            except Exception:
                logger.exception("Failed to fetch channel: %s", channel.telegram_url)

        return posts
    finally:
        await client.disconnect()


async def _ensure_authorized(client: TelegramClient, session_name: str) -> None:
    if await client.is_user_authorized():
        return

    logger.info("Telegram QR avtorizatsiyasi boshlanmoqda.")

    while True:
        try:
            qr_login = await client.qr_login()
            qr_path = _save_qr_code(qr_login.url, session_name)
            print("Telegram ilovasida Settings > Devices > Link Desktop Device orqali quyidagi QR-kodni skaner qiling:")
            print(qr_path)
            print(qr_login.url)

            await qr_login.wait()
            return
        except asyncio.TimeoutError:
            logger.warning("QR-kodning muddati tugadi. Yangi QR-kod yaratildi, iltimos yangisini skaner qiling.")
        except SessionPasswordNeededError:
            await _complete_two_factor_sign_in(client)
            return


async def _complete_two_factor_sign_in(client: TelegramClient) -> None:
    while True:
        password = getpass.getpass("Telegram 2 bosqichli parolini kiriting: ")
        try:
            await client.sign_in(password=password)
            return
        except PasswordHashInvalidError:
            logger.warning("2 bosqichli parol noto'g'ri. Qayta urinib ko'ring.")


def _save_qr_code(qr_url: str, session_name: str) -> Path:
    output_path = Path.cwd() / f"{Path(session_name).stem}_telegram_login_qr.png"
    image = qrcode.make(qr_url)
    image.save(output_path)
    return output_path.resolve()


async def _load_subscriber_count(client: TelegramClient, entity) -> int | None:
    try:
        full = await client(GetFullChannelRequest(entity))
        return full.full_chat.participants_count
    except Exception:
        logger.warning("Failed to load subscriber count for %s", getattr(entity, "title", entity))
        return None


async def _fetch_channel_posts(
    client: TelegramClient,
    entity,
    council_name: str,
    channel_url: str,
    subscriber_count: int | None,
    period: ReportPeriod,
) -> list[TelegramPost]:
    posts: list[TelegramPost] = []

    async for message in client.iter_messages(entity, offset_date=period.end):
        if not message.date:
            continue

        published_at = message.date.astimezone(period.start.tzinfo)
        if published_at < period.start:
            break

        if published_at > period.end:
            continue

        post = _message_to_post(
            council_name=council_name,
            channel_url=channel_url,
            subscriber_count=subscriber_count,
            message=message,
        )
        if post is not None:
            posts.append(post)

    return list(reversed(posts))


def _message_to_post(council_name: str, channel_url: str, subscriber_count: int | None, message) -> TelegramPost | None:
    text = (message.message or "").strip()
    has_media = bool(message.media)

    if has_media and not text:
        return None

    if not text:
        return None

    return TelegramPost(
        source_channel=council_name,
        source_url=channel_url,
        message_id=message.id,
        published_at=message.date,
        text=text,
        views=message.views,
        subscriber_count=subscriber_count,
        has_media=has_media,
    )
