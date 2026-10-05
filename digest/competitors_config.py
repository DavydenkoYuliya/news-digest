# -*- coding: utf-8 -*-
"""
Конфіг для competitor_digest.py — трек новин по виробниках-конкурентах МХП.
Без AI-класифікації: сутність і категорія визначаються через regex.

Щоб додати нового виробника:
  1. Додати новий блок у COMPETITORS (ключ — коротке ім'я, напр. "tyson").
  2. Створити файл feeds_<ключ>.txt (список RSS/Google News запитів).
  3. Додати ключ у PRODUCERS у run_digest_task.bat.
"""

# ================== СУТНОСТІ ПО ВИРОБНИКАХ ==================

COMPETITORS = {
    "pilgrims": {
        "display_name": "Pilgrim's Pride / JBS Group",
        # Назва холдингу для поля category на сайті — єдина для всіх сутностей нижче
        "holding": "Pilgrim's Pride",
        "feeds_file": "feeds_pilgrims.txt",
        "entities": [
            {
                "name": "Pilgrim's Pride Corporation",
                "short_name": "Pilgrim's Pride",
                "ticker": "NASDAQ:PPC",
                "country": "US",
                "parent_company": "JBS S.A.",
                "keywords": [r"pilgrim'?s pride", r"\bppc\b"],
            },
            {
                "name": "Pilgrim's UK",
                "short_name": "Pilgrim's UK",
                "ticker": "",
                "country": "UK",
                "parent_company": "Pilgrim's Pride Corporation",
                "keywords": [r"pilgrim'?s uk", r"pilgrim'?s europe"],
            },
            {
                "name": "Pilgrim's Food Masters",
                "short_name": "Pilgrim's Food Masters",
                "ticker": "",
                "country": "UK/IE",
                "parent_company": "Pilgrim's Pride Corporation",
                "keywords": [r"pilgrim'?s food masters", r"\bfood masters\b"],
            },
            {
                "name": "Moy Park",
                "short_name": "Moy Park",
                "ticker": "",
                "country": "UK/IE",
                "parent_company": "Pilgrim's Pride Corporation",
                "keywords": [r"moy park"],
            },
            {
                "name": "Pilgrim's Mexico",
                "short_name": "Pilgrim's Mexico",
                "ticker": "",
                "country": "MX",
                "parent_company": "Pilgrim's Pride Corporation",
                "keywords": [r"pilgrim'?s m[ée]xico", r"pilgrim'?s mexico"],
            },
            {
                # Скоуп-правило ТЗ: JBS враховуємо ТІЛЬКИ якщо є прямий зв'язок з PPC
                # (частка володіння, консолідація, спільні угоди, корпоративні дії щодо PPC)
                "name": "JBS S.A. (щодо PPC)",
                "short_name": "JBS",
                "ticker": "BVMF:JBSS3 / NYSE:JBS",
                "country": "BR",
                "parent_company": "",
                "keywords": [r"\bjbs\b"],
                "requires_context": [r"pilgrim'?s pride", r"\bppc\b"],
            },
        ],
    },
    "tyson": {
        "display_name": "Tyson Foods, Inc. (NYSE: TSN)",
        # Єдиний холдинг для групування на сайті (усі сегменти й бренди нижче)
        "holding": "Tyson Foods",
        "feeds_file": "feeds_tyson.txt",
        # УВАГА: Tyson — НЕ холдинг із юридично окремими новинними одиницями, а один
        # емітент (NYSE:TSN) з операційними СЕГМЕНТАМИ та портфелем БРЕНДІВ. Тому
        # "entities" тут = сегменти + бренди, а не дочірні компанії (як у Pilgrim's).
        "entities": [
            # --- Емітент (аналог "материнської" сутності Pilgrim's Pride Corp) ---
            {
                "name": "Tyson Foods, Inc.",
                "short_name": "Tyson Foods",
                "ticker": "NYSE:TSN",
                "country": "US",
                "parent_company": "",
                # Флагманський бренд "Tyson" покривається цією ж сутністю через \btyson\b —
                # окремим брендом не дублюємо.
                "keywords": [r"tyson foods", r"\btsn\b", r"\btyson\b"],
            },
            # --- Операційні сегменти ---
            # Це generic-слова (beef/pork/chicken), тому вимагають прямого контексту Tyson,
            # інакше "beef prices" від будь-кого потрапляв би в трек (та сама логіка, що JBS→PPC).
            {
                "name": "Tyson — Chicken segment",
                "short_name": "Tyson Chicken",
                "ticker": "",
                "country": "US",
                "parent_company": "Tyson Foods, Inc.",
                "keywords": [r"\bchicken\b", r"\bpoultry\b"],
                "requires_context": [r"\btyson\b", r"\btsn\b"],
            },
            {
                "name": "Tyson — Beef segment",
                "short_name": "Tyson Beef",
                "ticker": "",
                "country": "US",
                "parent_company": "Tyson Foods, Inc.",
                "keywords": [r"\bbeef\b", r"\bcattle\b"],
                "requires_context": [r"\btyson\b", r"\btsn\b"],
            },
            {
                "name": "Tyson — Pork segment",
                "short_name": "Tyson Pork",
                "ticker": "",
                "country": "US",
                "parent_company": "Tyson Foods, Inc.",
                "keywords": [r"\bpork\b", r"\bhogs?\b"],
                "requires_context": [r"\btyson\b", r"\btsn\b"],
            },
            {
                "name": "Tyson — Prepared Foods segment",
                "short_name": "Tyson Prepared Foods",
                "ticker": "",
                "country": "US",
                "parent_company": "Tyson Foods, Inc.",
                "keywords": [r"prepared foods"],
                "requires_context": [r"\btyson\b", r"\btsn\b"],
            },
            {
                "name": "Tyson — International/Other segment",
                "short_name": "Tyson International",
                "ticker": "",
                "country": "Global",
                "parent_company": "Tyson Foods, Inc.",
                "keywords": [r"international segment", r"tyson international"],
                "requires_context": [r"\btyson\b", r"\btsn\b"],
            },
            # --- Бренди портфеля: розрізняльні (proper nouns) — без вимоги контексту ---
            {
                "name": "Jimmy Dean",
                "short_name": "Jimmy Dean",
                "ticker": "",
                "country": "US",
                "parent_company": "Tyson Foods, Inc.",
                "keywords": [r"jimmy dean"],
            },
            {
                "name": "Hillshire Farm",
                "short_name": "Hillshire Farm",
                "ticker": "",
                "country": "US",
                "parent_company": "Tyson Foods, Inc.",
                "keywords": [r"hillshire farm", r"\bhillshire\b"],
            },
            {
                "name": "Aidells",
                "short_name": "Aidells",
                "ticker": "",
                "country": "US",
                "parent_company": "Tyson Foods, Inc.",
                "keywords": [r"aidells"],
            },
            {
                "name": "Wright Brand",
                "short_name": "Wright Brand",
                "ticker": "",
                "country": "US",
                "parent_company": "Tyson Foods, Inc.",
                # "Wright" сам по собі — надто поширене прізвище; тримаємо специфічні форми.
                "keywords": [r"wright brand", r"wright bacon"],
            },
            # --- Бренди-омоніми (загальновживані слова) — вимагають контексту Tyson ---
            {
                "name": "Ball Park",
                "short_name": "Ball Park",
                "ticker": "",
                "country": "US",
                "parent_company": "Tyson Foods, Inc.",
                "keywords": [r"ball park", r"ballpark"],
                "requires_context": [r"\btyson\b", r"\btsn\b", r"\bfrank"],
            },
            {
                "name": "State Fair",
                "short_name": "State Fair",
                "ticker": "",
                "country": "US",
                "parent_company": "Tyson Foods, Inc.",
                "keywords": [r"state fair"],
                "requires_context": [r"\btyson\b", r"\btsn\b", r"corn dog"],
            },
            {
                # IBP (Iowa Beef Packers) — м'ясний бренд/підрозділ Tyson; акронім неоднозначний.
                "name": "IBP",
                "short_name": "IBP",
                "ticker": "",
                "country": "US",
                "parent_company": "Tyson Foods, Inc.",
                "keywords": [r"\bibp\b"],
                "requires_context": [r"\btyson\b", r"\btsn\b", r"\bbeef\b", r"\bpork\b"],
            },
        ],
    },
    "brf": {
        "display_name": "BRF S.A. / MBRF Global Foods (B3: MBRF3, NYSE: BRFS)",
        # Після злиття Marfrig+BRF (вересень 2025) юрособа BRF влилась у MBRF Global
        # Foods. Наш фокус як поультрі-конкурента — BRF та бренди Sadia/Perdigão;
        # Marfrig (яловичина) враховуємо лише в контексті BRF/MBRF (як JBS→PPC).
        "holding": "BRF (MBRF Global Foods)",
        "feeds_file": "feeds_brf.txt",
        "entities": [
            {
                "name": "BRF S.A.",
                "short_name": "BRF",
                "ticker": "NYSE:BRFS / B3:BRFS3",
                "country": "BR",
                "parent_company": "MBRF Global Foods",
                "keywords": [r"brf s\.?a", r"\bbrf\b", r"brf global"],
            },
            {
                "name": "MBRF Global Foods",
                "short_name": "MBRF",
                "ticker": "B3:MBRF3",
                "country": "BR",
                "parent_company": "",
                "keywords": [r"\bmbrf\b", r"mbrf global"],
            },
            {
                "name": "Sadia",
                "short_name": "Sadia",
                "ticker": "",
                "country": "BR",
                "parent_company": "BRF S.A.",
                "keywords": [r"\bsadia\b"],
                # "sadia" — також прикметник (=здорова) і район міста (Sadia III,
                # Várzea Grande). Відкидаємо прикметникові колокації та муніципальний шум.
                "exclude": [
                    r"(?:mais|vida|alimenta[çc][ãa]o|mente|economia|concorr[êe]ncia|"
                    r"competi[çc][ãa]o|disputa|rivalidade|rela[çc][ãa]o|d[íi]eta|"
                    r"postura|pr[áa]tica|discuss[ãa]o|posi[çc][ãa]o)\s+(?:mais\s+)?sadi[ao]",
                    r"sadia\s+i{1,3}\b", r"tapa-buraco", r"patrulhamento",
                ],
            },
            {
                "name": "Perdigão",
                "short_name": "Perdigão",
                "ticker": "",
                "country": "BR",
                "parent_company": "BRF S.A.",
                "keywords": [r"perdig[ãa]o"],
                # "Perdigão" — ще й місто (MG) та прізвище. Відкидаємо омоніми:
                # фабрика устілок (palmilhas/EVA), Rosa Perdigão (acarajé/baiana/ekedi),
                # муніципальний контекст.
                "exclude": [
                    r"palmilha", r"\beva\b", r"acaraj[ée]", r"baiana", r"\bekedi\b",
                    r"rosa perdig", r"prefeitura de perdig", r"munic[íi]pio de perdig",
                    r"cidade de perdig",
                    # місто Perdigão/MG: локативне "em Perdigão" (бренд — "da Perdigão"/
                    # "Perdigão Na Brasa"), місцева індустрія, вказівка штату MG.
                    r"em perdig[ãa]o\b", r"ind[úu]stria em perdig",
                    r"perdig[ãa]o[\s/,\-]*mg\b",
                ],
            },
            {
                "name": "Qualy",
                "short_name": "Qualy",
                "ticker": "",
                "country": "BR",
                "parent_company": "BRF S.A.",
                "keywords": [r"\bqualy\b"],
            },
            {
                "name": "Banvit",
                "short_name": "Banvit",
                "ticker": "",
                "country": "TR",
                "parent_company": "BRF S.A.",
                "keywords": [r"\bbanvit\b"],
            },
            {
                # Perdix — експортний бренд BRF; слово також рід куріпок, тому контекст.
                "name": "Perdix",
                "short_name": "Perdix",
                "ticker": "",
                "country": "BR",
                "parent_company": "BRF S.A.",
                "keywords": [r"\bperdix\b"],
                "requires_context": [r"\bbrf\b", r"\bsadia\b", r"export", r"halal"],
            },
            {
                "name": "Kidelli",
                "short_name": "Kidelli",
                "ticker": "",
                "country": "BR",
                "parent_company": "BRF S.A.",
                "keywords": [r"\bkidelli\b"],
            },
            {
                # Marfrig (яловичина) — материнська структура MBRF; враховуємо лише
                # за прямого звʼязку з BRF/поультрі-активами (як JBS у треку Pilgrim's).
                "name": "Marfrig (щодо BRF)",
                "short_name": "Marfrig",
                "ticker": "B3:MRFG3",
                "country": "BR",
                "parent_company": "",
                "keywords": [r"\bmarfrig\b"],
                "requires_context": [r"\bbrf\b", r"\bmbrf\b", r"\bsadia\b", r"perdig[ãa]o"],
            },
        ],
    },
    "ldc_groupe": {
        "display_name": "Groupe LDC / L.D.C. S.A. (Euronext: LOUP)",
        "holding": "Groupe LDC",
        "feeds_file": "feeds_ldc_groupe.txt",
        # Французький лідер з виробництва птиці. "LDC" — вкрай неоднозначна абревіатура
        # (Louis Dreyfus, least developed countries), тому корпоративна сутність має
        # exclude на Dreyfus/LDCs. Багато брендів — загальні слова → контекст/мінус-слова.
        "entities": [
            {
                "name": "Groupe LDC (L.D.C. S.A.)",
                "short_name": "Groupe LDC",
                "ticker": "EURONEXT:LOUP",
                "country": "FR",
                "parent_company": "",
                "keywords": [r"groupe ldc", r"\bl\.d\.c\b", r"\bldc\b"],
                "exclude": [r"louis[\s-]?dreyfus", r"\bdreyfus\b",
                            r"least developed countr", r"\bldcs\b"],
            },
            {
                "name": "Le Gaulois",
                "short_name": "Le Gaulois", "ticker": "", "country": "FR",
                "parent_company": "Groupe LDC",
                "keywords": [r"le gaulois"],
            },
            {
                "name": "Maître CoQ",
                "short_name": "Maître CoQ", "ticker": "", "country": "FR",
                "parent_company": "Groupe LDC",
                "keywords": [r"ma[îi]tre coq"],
            },
            {
                "name": "Loué (Fermiers de Loué)",
                "short_name": "Loué", "ticker": "", "country": "FR",
                "parent_company": "Groupe LDC",
                # "loué" = також "орендований/хвалений"; тримаємо контекст птиці/бренду.
                "keywords": [r"fermiers de lou[ée]", r"volailles? de lou[ée]",
                             r"poulet.{0,10}lou[ée]", r"lou[ée] label"],
            },
            {
                "name": "Marie (traiteur)",
                "short_name": "Marie", "ticker": "", "country": "FR",
                "parent_company": "Groupe LDC",
                # "Marie" — надто поширене ім'я; лише в кулінарно-брендовому контексті.
                "keywords": [r"\bmarie\b"],
                "requires_context": [r"\bldc\b", r"traiteur", r"surgel", r"plat cuisin",
                                     r"marque marie"],
                "exclude": [r"sainte?[\s-]marie", r"marie curie", r"marie[\s-]claire"],
            },
            {
                "name": "Volailles Le Fleuron",
                "short_name": "Le Fleuron", "ticker": "", "country": "FR",
                "parent_company": "Groupe LDC",
                "keywords": [r"le fleuron"],
                "requires_context": [r"\bldc\b", r"volaill", r"poulet"],
            },
            {
                "name": "Bio Bresse",
                "short_name": "Bio Bresse", "ticker": "", "country": "FR",
                "parent_company": "Groupe LDC",
                "keywords": [r"bio bresse"],
            },
        ],
    },
    "louis_dreyfus": {
        "display_name": "Louis Dreyfus Company (LDC) — ABCD agri-trader",
        "holding": "Louis Dreyfus Company",
        "feeds_file": "feeds_louis_dreyfus.txt",
        # Глобальний трейдер/переробник агросировини (зерно, олійні, цукор, кава, сік…).
        # 45% — ADQ (Абу-Дабі) з 2021. Приватна (торгуються облігації). Товарні лінії =
        # generic-слова (wheat/sugar/coffee), тому вимагають контексту Louis Dreyfus/LDC.
        "entities": [
            {
                "name": "Louis Dreyfus Company",
                "short_name": "Louis Dreyfus", "ticker": "", "country": "NL",
                "parent_company": "",
                "keywords": [r"louis[\s-]?dreyfus"],
                # Джулія Луї-Дрейфус (акторка) — не компанія.
                "exclude": [r"julia louis", r"seinfeld", r"\bveep\b", r"actress"],
            },
            {
                "name": "LDC — Grains & Oilseeds",
                "short_name": "LDC Grains & Oilseeds", "ticker": "", "country": "Global",
                "parent_company": "Louis Dreyfus Company",
                "keywords": [r"grains? and oilseeds?", r"grains? & oilseeds?",
                             r"\bwheat\b", r"\bsoybean", r"\bcorn\b", r"oilseed"],
                "requires_context": [r"louis[\s-]?dreyfus", r"\bldc\b"],
            },
            {
                "name": "LDC — Sugar",
                "short_name": "LDC Sugar", "ticker": "", "country": "Global",
                "parent_company": "Louis Dreyfus Company",
                "keywords": [r"\bsugar\b", r"ethanol"],
                "requires_context": [r"louis[\s-]?dreyfus", r"\bldc\b"],
            },
            {
                "name": "LDC — Coffee",
                "short_name": "LDC Coffee", "ticker": "", "country": "Global",
                "parent_company": "Louis Dreyfus Company",
                "keywords": [r"\bcoffee\b"],
                "requires_context": [r"louis[\s-]?dreyfus", r"\bldc\b"],
            },
            {
                "name": "LDC — Juice",
                "short_name": "LDC Juice", "ticker": "", "country": "Global",
                "parent_company": "Louis Dreyfus Company",
                "keywords": [r"\bjuice\b", r"orange juice", r"\bfcoj\b"],
                "requires_context": [r"louis[\s-]?dreyfus", r"\bldc\b"],
            },
            {
                "name": "LDC — Cotton",
                "short_name": "LDC Cotton", "ticker": "", "country": "Global",
                "parent_company": "Louis Dreyfus Company",
                "keywords": [r"\bcotton\b"],
                "requires_context": [r"louis[\s-]?dreyfus", r"\bldc\b"],
            },
            {
                # ADQ — власник 45%; враховуємо лише в контексті LDC (як Marfrig→BRF).
                "name": "ADQ (щодо LDC)",
                "short_name": "ADQ", "ticker": "", "country": "AE",
                "parent_company": "",
                "keywords": [r"\badq\b"],
                "requires_context": [r"louis[\s-]?dreyfus", r"\bldc\b"],
            },
        ],
    },
    "jbs": {
        "display_name": "JBS N.V. / JBS S.A. (NYSE: JBS, B3: JBSS32)",
        "holding": "JBS",
        "feeds_file": "feeds_jbs.txt",
        # Найбільша у світі мʼясна компанія (Бразилія/Нідерланди). Ключове для МХП —
        # Seara (птиця/свинина). Pilgrim's/Moy Park — дочірні JBS (перетин із треком #1,
        # це очікувано). Омоніми Seara (місто/«на ниві…») та Swift (Taylor Swift/SWIFT/
        # мова) мають exclude/контекст. PT-шар таксономії вже підключено (спільний з BRF).
        "entities": [
            {
                "name": "JBS N.V. / JBS S.A.",
                "short_name": "JBS", "ticker": "NYSE:JBS / B3:JBSS32", "country": "BR",
                "parent_company": "",
                "keywords": [r"\bjbs\b", r"jbs n\.?v", r"jbs s\.?a", r"jbs foods"],
            },
            {
                "name": "Seara",
                "short_name": "Seara", "ticker": "", "country": "BR",
                "parent_company": "JBS N.V.",
                "keywords": [r"\bseara\b"],
                # "seara" = також місто (SC) і фігуральне «на ниві/у сфері».
                "exclude": [
                    r"\bna seara d[aeo]s?\b",  # фігуральне «na seara da política/do direito»
                    r"seara (?:pol[íi]tica|jur[íi]dica|esportiva|liter[áa]ria|"
                    r"acad[êe]mica|econ[óo]mica|digital|do direito|da sa[úu]de|cultural)",
                    r"munic[íi]pio de seara", r"prefeitura de seara",
                ],
            },
            {
                "name": "Friboi",
                "short_name": "Friboi", "ticker": "", "country": "BR",
                "parent_company": "JBS N.V.",
                "keywords": [r"\bfriboi\b", r"\bmaturatta\b"],
            },
            {
                "name": "Swift (JBS)",
                "short_name": "Swift", "ticker": "", "country": "BR",
                "parent_company": "JBS N.V.",
                # надто багатозначне слово → лише в мʼясному/JBS контексті + мінус-слова.
                "keywords": [r"\bswift\b"],
                "requires_context": [r"\bjbs\b", r"beef", r"\bpork\b", r"\bmeat\b",
                                     r"\bcarne\b", r"friboi", r"a[çc]ougue"],
                "exclude": [r"taylor swift", r"swift code", r"swift current",
                            r"swift transportation",
                            r"\bswift\b.{0,12}(?:payment|bank|network|messaging|transfer|iban)",
                            r"programming|xcode|\bios app"],
            },
            {
                "name": "Pilgrim's Pride (JBS)",
                "short_name": "Pilgrim's Pride", "ticker": "NASDAQ:PPC", "country": "US",
                "parent_company": "JBS N.V.",
                "keywords": [r"pilgrim'?s pride", r"\bppc\b"],
            },
            {
                "name": "Moy Park (JBS)",
                "short_name": "Moy Park", "ticker": "", "country": "UK/IE",
                "parent_company": "JBS N.V.",
                "keywords": [r"moy park"],
            },
            {
                "name": "JBS USA (Beef/Pork North America)",
                "short_name": "JBS USA", "ticker": "", "country": "US",
                "parent_company": "JBS N.V.",
                "keywords": [r"jbs usa", r"beef north america", r"pork usa"],
                "requires_context": [r"\bjbs\b"],
            },
            {
                "name": "JBS Australia",
                "short_name": "JBS Australia", "ticker": "", "country": "AU",
                "parent_company": "JBS N.V.",
                "keywords": [r"jbs australia", r"\bprimo\b", r"\bhuon\b", r"rivalea"],
                "requires_context": [r"\bjbs\b", r"australia", r"aquaculture", r"salmon",
                                     r"smallgoods", r"bacon"],
            },
        ],
    },
    # producer #7+ додаються сюди за тим самим шаблоном
}

# ================== ТАКСОНОМІЯ ПОДІЙ (без AI) ==================

EVENT_CATEGORIES = {
    "фінанси": [
        r"earnings", r"revenue", r"quarterly results", r"profit", r"net income",
        r"stock (?:price|closes?|falls?|rises?|drops?)", r"share price",
        r"dividend", r"analyst", r"price target", r"consensus rating",
        r"guidance", r"market cap",
        r"stock (?:surg\w+|slid\w+|jumps?|rally|rallies|climbs?|gains?|sinks?|dips?|"
        r"trading up|trading down|underperform\w*|outperform\w*)",
        r"\brating\b", r"undervalued", r"overvalued", r"valuation", r"bargain",
        r"trending stock", r"consensus",
        r"\bf?q[1-4]\b", r"(?:first|second|third|fourth)[\s-]quarter",
        r"quarterly (?:income|profit|loss)", r"\bresults\b", r"\beps\b",
        r"earnings per share", r"\b10-[qk]\b", r"(?:miss|beat)\w*\s+(?:estimates|expectations)",
        r"\boutlook\b", r"full-year", r"\bsales\b", r"restructuring",
        r"upgrade[sd]?", r"downgrade[sd]?", r"\brsus?\b", r"\bvolumes?\b",
    ],
    "M&A": [
        r"acquisit", r"acquire[sd]?\b", r"merger", r"\bstake\b", r"divest",
        r"takeover", r"buyout", r"joint venture", r"consolidat",
    ],
    "операційна діяльність": [
        r"\bplant\b", r"facility", r"production line", r"expansion",
        r"capacity", r"\boutput\b", r"recall", r"processing plant",
        r"new (?:facility|plant|line|production line)", r"closure", r"shutdown",
        r"opens? (?:a )?(?:new )?(?:plant|facility|line|processing)",
        r"(?:plant|facility) (?:opening|expansion|closure|closing)",
        r"groundbreaking", r"break ground", r"reopen",
        r"layoffs?", r"lay off", r"job cuts", r"\bidle\b",
        r"feed cost", r"feed prices?", r"grain prices?", r"corn prices?",
        r"soybean", r"soymeal", r"input cost", r"hedg(?:e|ing|ed)", r"throughput",
    ],
    "надзвичайні події": [
        r"explosion", r"\bblast\b", r"\bfire\b", r"\bblaze\b", r"accident",
        r"injur(?:y|ed|ies)", r"fatalit", r"\bdeaths?\b", r"\bkilled\b",
        r"evacuat", r"hazmat", r"ammonia leak", r"\bspill\b", r"\bincident\b",
        r"contaminat", r"outbreak", r"salmonella", r"listeria", r"e\.?\s?coli",
        r"\bosha\b", r"emergency", r"worker (?:killed|injured|dies|hurt)",
    ],
    "регуляторика": [
        r"regulat", r"\bpermit\b", r"compliance", r"inspection",
        r"\busda\b", r"\bfda\b", r"\bepa\b", r"\bniea\b", r"\bdaera\b",
        r"environmental permit", r"food safety", r"\bfsis\b", r"line speed",
    ],
    "судові справи": [
        r"lawsuit", r"\bcourt\b", r"litigation", r"\bsue[sd]?\b",
        r"legal action", r"settlement", r"petition.*court", r"class action",
    ],
    "кадри": [
        r"\bappoint", r"\bceo\b", r"executive", r"board of directors",
        r"\bhire[sd]?\b", r"resign", r"chief .*officer", r"names? .* as",
        r"steps down",
    ],
    "продукти": [
        r"product launch", r"rebrand", r"new product", r"brand identity",
        r"nugget", r"lineup", r"packaging redesign", r"product line",
        r"new line", r"new flavou?r", r"limited edition", r"menu item",
        r"cultivated meat", r"cultured meat", r"lab.grown", r"cell.based",
        r"alternative protein", r"plant.based", r"ready.to.eat", r"\brte\b",
        r"foodservice (?:deal|contract)", r"supply (?:deal|agreement|contract)",
        r"private label", r"(?:wins?|lost|loses?) .{0,20}contract",
    ],
    "маркетинг": [
        r"marketing (?:plan|strategy|campaign|push)", r"ad campaign",
        r"advertis", r"rebrand", r"brand refresh", r"sponsorship",
        r"super bowl ad", r"brand (?:identity|relaunch)", r"\bcampaign\b",
        r"giveaway", r"gives? away", r"sweepstakes", r"season tickets", r"promotion",
    ],
    "технології/автоматизація": [
        r"automation", r"\brobot", r"robotic", r"artificial intelligence",
        r"machine vision", r"computer vision", r"digital twin", r"\boee\b",
        r"deboning", r"automated (?:line|plant)", r"predictive maintenance",
    ],
    "експорт/ринки збуту": [
        r"\bhpai\b", r"avian (?:influenza|flu)", r"bird flu", r"h5n1",
        r"export (?:ban|permit|market|sales|deal)", r"import ban",
        r"market access", r"trade (?:deal|barrier|dispute)", r"\btariff",
        r"port (?:delay|congestion)", r"cold chain", r"\breefer\b",
        r"ocean freight", r"freight rate", r"container ship",
        r"cattle (?:import|shipment)s?", r"resume.{0,20}(?:cattle|shipment)",
        r"approves?.{0,20}cattle", r"shipments? from",
        r"\bhalal\b", r"export (?:ban|suspension|permit|licen[cs]e)", r"import ban",
    ],
    "робоча сила": [
        r"\bstrike\b", r"\bunion\b", r"walkout", r"picket", r"labor shortage",
        r"worker shortage", r"staffing", r"wage (?:increase|hike)",
        r"hourly (?:pay|wage)", r"\bmigrant", r"immigration raid", r"workforce",
    ],
    "ESG": [
        r"net.zero", r"sustainab", r"emission", r"deforestation",
        r"greenpeace", r"\besg\b", r"\bcarbon\b", r"animal welfare",
        r"environmental", r"cerrado", r"amaz[ôo]nia",
        r"amazon (?:rainforest|biome|deforestation|forest)", r"soy moratorium",
    ],
}

# ============ ПОРТУГАЛОМОВНИЙ ШАР (BRF та ін. бразильські/латам виробники) ============
# Без цього pt-BR новини майже повністю падають у "інше" (заголовки не матчаться з
# англ. keywords). Розширює наявні категорії тими самими ключами — нових не створює.
_EVENT_CATEGORIES_PT = {
    "фінанси": [
        r"lucro", r"receita", r"preju[íi]zo", r"dividendo", r"\ba[çc][õo]es\b",
        r"em (?:queda|alta|baixa)", r"despenca", r"dispara", r"balan[çc]o",
        r"resultado", r"pre[çc]o-alvo", r"recomenda[çc][ãa]o", r"ibovespa",
        r"lucro l[íi]quido", r"faturamento", r"margem", r"\bebitda\b",
        r"favorita do setor",
    ],
    "M&A": [
        r"aquisi[çc][ãa]o", r"fus[ãa]o", r"incorpora[çc][ãa]o",
        r"participa[çc][ãa]o societ[áa]ria", r"venda de ativos", r"cis[ãa]o",
    ],
    "операційна діяльність": [
        r"f[áa]brica", r"planta industrial", r"unidade industrial", r"amplia[çc][ãa]o",
        r"expans[ãa]o", r"capacidade", r"linha de produ[çc][ãa]o", r"fechamento",
        r"produ[çc][ãa]o", r"investimento", r"inaugura", r"nova unidade",
    ],
    "надзвичайні події": [
        r"inc[êe]ndio", r"explos[ãa]o", r"vazamento", r"am[óo]nia", r"acidente",
        r"evacua[çc][ãa]o", r"contamina[çc][ãa]o", r"surto", r"\bmorte", r"ferido",
    ],
    "регуляторика": [
        r"regula[çc]", r"\banvisa\b", r"\bmapa\b", r"fiscaliza[çc][ãa]o",
        r"inspe[çc][ãa]o", r"licen[çc]a", r"seguran[çc]a alimentar", r"recolhimento",
    ],
    "судові справи": [
        r"processo judicial", r"a[çc][ãa]o judicial", r"\bjusti[çc]a\b", r"liminar",
        r"acordo judicial", r"\bmulta\b", r"condena[çc][ãa]o",
    ],
    "кадри": [
        r"nomeia", r"executivo", r"conselho de administra[çc][ãa]o", r"ren[úu]ncia",
        r"demite", r"diretor-presidente", r"novo (?:ceo|presidente|diretor)",
    ],
    "продукти": [
        r"lan[çc]amento", r"novo produto", r"linha de produtos", r"embalagem",
        r"\bsabor\b", r"novidade", r"edi[çc][ãa]o limitada", r"colecion[áa]vel",
    ],
    "маркетинг": [
        r"campanha", r"publicidade", r"propaganda", r"patroc[íi]nio", r"rebranding",
        r"mais escolhida", r"marca mais", r"garoto-propaganda",
    ],
    "технології/автоматизація": [
        r"automa[çc][ãa]o", r"rob[óo]tica", r"intelig[êe]ncia artificial",
        r"digitaliza[çc][ãa]o", r"\bia\b",
    ],
    "експорт/ринки збуту": [
        r"exporta[çc][ãa]o", r"importa[çc][ãa]o", r"embargo", r"tarifa",
        r"gripe avi[áa]ria", r"influenza avi[áa]ria", r"acesso a mercado",
        r"porto de santos", r"habilita[çc][ãa]o", r"\bhalal\b",
    ],
    "робоча сила": [
        r"greve", r"sindicato", r"demiss[õo]es", r"\bsal[áa]rio", r"m[ãa]o de obra",
    ],
    "ESG": [
        r"sustentabilidade", r"emiss[õo]es", r"desmatamento", r"bem-estar animal",
        r"carbono", r"cerrado", r"amaz[ôo]nia",
    ],
}
for _k, _v in _EVENT_CATEGORIES_PT.items():
    EVENT_CATEGORIES.setdefault(_k, []).extend(_v)

# ============ ФРАНКОМОВНИЙ ШАР (Groupe LDC та ін. французькі виробники) ============
_EVENT_CATEGORIES_FR = {
    "фінанси": [
        r"chiffre d'affaires", r"b[ée]n[ée]fice", r"r[ée]sultat net", r"dividende",
        r"cours de bourse", r"en bourse", r"le titre", r"objectif de cours",
        r"recommandation", r"\bmarge", r"rentabilit[ée]", r"\bebitda\b",
    ],
    "M&A": [
        r"acquisition", r"fusion", r"rachat", r"cession", r"prise de participation",
        r"reprise de", r"co-entreprise",
    ],
    "операційна діяльність": [
        r"\busine\b", r"site de production", r"abattoir", r"capacit[ée]",
        r"extension", r"agrandissement", r"fermeture", r"production",
        r"investit", r"investissement", r"inaugure", r"ligne de production",
        r"nouveau site", r"modernisation",
    ],
    "надзвичайні події": [
        r"incendie", r"explosion", r"fuite d'ammoniac", r"accident", r"[ée]vacuation",
        r"contamination", r"[ée]pid[ée]mie", r"\bmort", r"bless[ée]", r"intoxication",
    ],
    "регуляторика": [
        r"r[ée]glementation", r"\bdgal\b", r"\banses\b", r"contr[ôo]le sanitaire",
        r"inspection", r"autorisation", r"s[ée]curit[ée] alimentaire", r"\brappel\b",
    ],
    "судові справи": [
        r"proc[èe]s", r"tribunal", r"\bjustice\b", r"plainte", r"condamnation",
        r"\bamende\b", r"contentieux",
    ],
    "кадри": [
        r"\bnomme\b", r"nomination", r"\bpdg\b", r"directeur g[ée]n[ée]ral",
        r"conseil d'administration", r"d[ée]mission", r"dirigeant",
    ],
    "продукти": [
        r"lancement", r"nouveau produit", r"\bgamme\b", r"nouvelle recette",
        r"innovation produit",
    ],
    "маркетинг": [
        r"campagne", r"publicit[ée]", r"parrainage", r"sponsoring", r"la marque",
    ],
    "технології/автоматизація": [
        r"automatisation", r"robotique", r"intelligence artificielle",
        r"num[ée]risation",
    ],
    "експорт/ринки збуту": [
        r"exportation", r"importation", r"embargo", r"grippe aviaire",
        r"influenza aviaire", r"\bfavi\b", r"march[ée] export", r"tarif douanier",
        r"\bdouane", r"acc[èe]s au march[ée]",
    ],
    "робоча сила": [
        r"\bgr[èe]ve\b", r"syndicat", r"licenciement", r"\bsalaire", r"main-d'œuvre",
        r"plan social",
    ],
    "ESG": [
        r"durabilit[ée]", r"[ée]missions", r"bien-[êe]tre animal", r"d[ée]forestation",
        r"\bcarbone\b", r"empreinte",
    ],
}
for _k, _v in _EVENT_CATEGORIES_FR.items():
    EVENT_CATEGORIES.setdefault(_k, []).extend(_v)

RELEVANCE_SCORE_MAP = {"висока": 8, "середня": 5, "низька": 2}
