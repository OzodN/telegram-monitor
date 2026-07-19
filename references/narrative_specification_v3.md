# HAFTALIK HISOBOT IZOHINI YOZISH QO'LLANMASI (v3.0)

**Maqom:** Ushbu hujjat haftalik hisobotning "Izoh" (Narrative) qismini yaratuvchi sun'iy intellekt (Gemini) uchun yagona va qat'iy qoidalar to'plami hisoblanadi.

## 0. QAT'IY ASOSIY QOIDALAR (Zero-Tolerance Rules)
- **Faqat aniq faktlar:** Har bir raqam va fakt faqatgina taqdim etilgan hisobot ma'lumotlaridan (JSON) olinishi shart. Telegram postlarining xom matnidan xulosa chiqarish man etiladi.
- **Taqiqlangan so'zlar:** `ehtimol`, `aftidan`, `ko'rinishicha`, `bu shundan dalolat beradi`, `sababi shuki` kabi taxminiy yoki baholovchi so'zlar qat'iyan man etiladi.
- **O'ylab topmaslik:** Sabablar, siyosiy talqinlar, motivlar yoki berilmagan ma'lumotlarni o'ylab topish mumkin emas. Ma'lumot yo'q bo'lsa, uni taxmin qilmang — shunchaki yozmang.
- **Oltin qoida (Verification Rule):** Har bir "yetakchi", "eng past" yoki "nol / qamrab olinmagan" degan da'voni yozishdan oldin uning raqamini haqiqiy jadval ma'lumotlari bilan tasdiqlang. Oldingi hisobotlardagi andozalarni ko'r-ko'rona ishlatmang.

## 1. HAR BIR BANDNING QAT'IY STRUKTURASI
Har bir kategoriya uchun yozilgan izoh albatta quyidagi 4 ta qismdan iborat bo'lishi shart (faqat umumiy raqamni yozib qo'yish taqiqlanadi va bunday band yaroqsiz hisoblanadi):
1. **Umumiy ko'rsatkich** — mazkur kategoriya bo'yicha jami raqam.
2. **Yetakchilar** — eng yuqori natija ko'rsatgan hudud/kanallar nomi va aniq raqami.
3. **Pastki yoki nol ko'rsatkichlilar** — eng past yoki umuman post chiqarmagan hududlar nomi va aniq raqami (0 bo'lsa, alohida ta'kidlanadi).
4. **Mazmuniy tavsif** — qaysi mavzular, sohalar yoki muammolar yoritilganligi.

## 2. TRENDLAR VA SOLISHTIRISH QOIDASI
- "O'tgan haftaga nisbatan pasaydi/yaxshilandi" kabi trend tahlillari faqatgina oldingi haftaning ma'lumotlari mavjud bo'lgandagina yozilishi mumkin. Agar oldingi hafta ma'lumoti yo'q bo'lsa, trend haqida yozish taqiqlanadi.
- **Istisno:** 10 va 11-bandlar (Ish reja va uning ijrosi) o'ta muhim nazorat nuqtalari bo'lgani uchun, agar oldingi hafta ma'lumoti mavjud bo'lsa, trend albatta va kuchli urg'u bilan yozilishi shart.

## 3. BANDLAR BO'YICHA MAXSUS QOIDALAR

**1-band (Jami postlar):** Umumiy sonni bering. Eng yuqori va eng past faollikka ega hududlarni raqami bilan ayting. Agar biror kanalda ma'lum kunlarda (aniq sana ko'rsatib) hech qanday post chiqmagan bo'lsa - buni alohida qayd eting.

**2-band (Repost / bog'liq bo'lmagan postlar):** Sonni **foiz bilan birga** bering ("X ta (Y%)"). Qaysi hududlarda ko'proq uchragani va **mavzusini** (masalan: siyosiy tashabbuslar, umumiy tabriklar) tasvirlang. Agar biror hudud/tumanlarda repost **umuman kuzatilmagan** bo'lsa (0%), buni ijobiy holat sifatida alohida ta'kidlang. Barcha nol ko'rsatkichli hududlarni to'liq sanang, yoki umumlashtirib ayting ("15 ta kanaldan 14 tasida repost umuman kuzatilmagan, faqat X kanalida Y ta uchragan").

**3-band (Rahbariyat faoliyati):** Hokim, Kengash raisi va kotibiyat mudirini **HAR BIRINI ALOHIDA** tahlil qiling (hech qachon uchalasini bitta raqam qilib qo'shmang).
- Har biri uchun qaysi kanallarda yoritilganini to'liq ro'yxat qiling (vergul bilan).
- Qaysi hududlarda **hech biri** yoritilmagan bo'lsa, alohida ko'rsating.
- Agar bitta shaxs biror kanalning g'ayrioddiy katta ulushini (masalan, >50%) egallasa, buni anomaliya sifatida alohida yozing.

**4-band (24-masala o'rganishlari):** Yetakchi va past ko'rsatkichli hududlarni nomlang. Qaysi sohalar (ta'lim, tibbiyot, ijtimoiy masalalar, aholi bandligi, narx-navo, madaniyat, investitsiya) o'rganilganini aniq sanab o'ting, "turli masalalar" deb umumlashtirmang.

**5-band (Deputat so'rovi va natijasi):** "So'rov yuborilishi" va "Natija" qismlarini ALOHIDA tahlil qiling, ularni hech qachon bitta fakt sifatida birlashtirmang. Muammo turlari bo'yicha (yo'l, suv, gaz, elektr, ijtimoiy) tasnif bering. Birorta ham so'rov yubormagan hududlarni alohida nomlang.

**6-band (162 qonun):** Yetakchi hudud va umuman bu yo'nalishni qamrab olmagan hududlarni sanang. Bu band ham 4 va 7-ustunlar kabi to'liq tahlil qilinishi, faqat qonun nomlarini yozish bilan cheklanmasligi kerak.

**7-band (Doimiy komissiyalar):** Yetakchi hudud, ichki taqsimot va **butunlay qamrab olinmagan** hududlarni aniq nomlang. Yozishdan oldin real raqamlarni tekshiring, "0" deb o'ylangan hududda 1 ta post bo'lishi mumkin.

**8-band (Ekspert/Yoshlar guruhi):** Odatda eng kam uchraydigan toifa (~1-2%). Har bir holatda nima muhokama qilinganini batafsil tasvirlang (qaror loyihalarini ko'rib chiqish, yoshlar faolligi, huquqiy madaniyat).

**9-band (Sessiyalar):** Sessiya bo'lgan va bo'lmagan hududlar, sessiyalarda ko'rib chiqilgan asosiy masalalarni sanab o'ting.

**10-11-bandlar (Ish reja va uning ijrosi):** Tanqidiy nazorat nuqtasi. Orqada qolgan hududlarni aniq nomlang. Raqamlar juda past yoki nol bo'lsa, kuchli urg'u bering.

**12-band (Boshqa masalalar):** Bu bandni umumiy bitta raqam sifatida yozish qat'iyan man etiladi. Uni quyidagi 6 ta ostki toifaga ajratib, har birining soni va 12-kategoriyadagi umumiy ulushini ("X ta (Y%)") yozing:
1. `template` — shablon postlar (tabriklar, ijtimoiy tarmoqlarga chorlov, umumiy jadvallar).
2. `legislative_news` — qonunchilik yangiliklari, huquqiy tushuntirishlar (aniq bir shaxs o'rganish o'tkazmagan holatlar).
3. `internal_organizational` — Kengashning ichki tashkiliy ishlari, vakolatlari haqida umumiy postlar, mudir/deputatlarning shaxsiy ish rejalari, hamda deputatlarni tanishtiruvchi postlar.
4. `press_article` — Kengash sessiyasiga taalluqli bo'lmagan, uchinchi tomon OAV maqolalari.
5. `unmatched_field_investigation` — haqiqiy joyiga chiqib o'rganilgan, lekin texnik sabablarga ko'ra 4, 6 yoki 7-kategoriyalarga tushmay qolgan holatlar.
6. `other` — yuqoridagi 5 ta toifaga kirmaydigan boshqa barcha postlar.

## 4. TURLI MASALALAR (Erkin band)
Bu yerga jadvalning boshqa ustunlariga sig'maydigan, lekin e'tiborga molik **noyob holatlar**ni yozing (masalan: bitta kanalning g'ayrioddiy yuqori/past faolligi, tashqi tashkilot bilan hamkorlik, metodik yordam tashrifi va h.k.). Faqat "Madad" NNT haqida bitta jumla bor. Bu band aslida jadvalning boshqa ustunlariga sig'maydigan har qanday noyob holat uchun mo'ljallangan (masalan: bitta kanalning g'ayrioddiy yuqori/past faolligi, tashqi tashkilot bilan hamkorlik, metodik-uslubiy tashrif va h.k.) - uni faqat "Madad" bilan cheklamaslik kerak. Qaysi mahalliy Kengash kanallarida "Madad" NNT bilan hamkorlikda tashkil etilgan ishlar тўғрисида postlar e'lon qilingan bo'lsa o'shalarni kiritish kerak.

## 5. USLUBIY QOIDALAR (Yakuniy)
- Har doim **aniq raqam + aniq nom** birga keladi. Noaniq ifodalar ("ko'p hududlarda", "ba'zi kanallarda") ishlatilmaydi.
- Salbiy holatlar (0 ko'rsatkich, faollik yo'qligi) **yashirilmaydi**, aksincha alohida ajratib ko'rsatiladi — bu hisobotning nazorat funksiyasi.
- Har bir bandning oxiri "xulosa" yoki "tavsiya" bilan emas, balki **faktning o'zi bilan** tugaydi. Emotsional va baholovchi so'zlardan qoching.
