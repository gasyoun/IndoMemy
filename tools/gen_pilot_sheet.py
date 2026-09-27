#!/usr/bin/env python3
"""Generate the MG approval sheet for the SufferingMahabharata meme cards.

Committed generator (the H2929 lesson): the hub copy at gasyoun.github.io/vote/sheets/
is archival; this script is the regen path. Emitter: csl-pyutil render_review_sheet.

Usage:
  python3 tools/gen_pilot_sheet.py batch1   # партия 1: 7 утверждённых карт, sheet на фрагментах (27-09-2026)
  python3 tools/gen_pilot_sheet.py batch2   # партия 2: 10 новых карт (7/2/1), sheet на фрагментах

Партия 1 (26-09-2026) голосовалась MG по МАСТЕРАМ; лист batch1 — подтверждение
ФРАГМЕНТОВ (формат 27-09) перед постингом: red line №3 «ноль постов без
утверждения MG». Подпись варианта А = утверждённая MG (она же основная в
memes.tsv); партия 2 генерится сразу на фрагментах (H5529).
"""
import csv
import os
import sys

from csl_pyutil.review_sheet import render_review_sheet
from csl_pyutil.evidence import EvidenceManifest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = "https://raw.githubusercontent.com/gasyoun/SufferingMahabharata/main/"

# Вариант А всегда зеркалит основную подпись в memes.tsv (для партии 1 —
# утверждённую MG 26-09-2026; порядок вариантов обновлён под выбор MG).
CAPTIONS = {
    "SM-001": ["Понедельник: все задачи в статусе «горит»",
               "Выкатили релиз в пятницу — разобрались к среде",
               "Когда пришёл на планёрку, а там уже все"],
    "SM-002": ["Спамеров нашли. Отпустили с почётом",
               "Отдел безопасности поймал двоих, кто пересылал мемы мимо рабочего чата",
               "Обнаружили двух коллег, которые все пять лет работали ни разу не написав в общий чат"],
    "SM-003": ["Тимбилдинг прошёл активно",
               "Когда вся компания бросила дела на один общий дедлайн",
               "Итоги квартала подводим все вместе"],
    "SM-004": ["Разбудили Кумбхакарну. Зря.",
               "Будильник прозвенел в 6:00. Кумбхакарна проиграл",
               "«Ещё пять минут» — год Five Minutes Later"],
    "SM-005": ["Утвердил повестку. Повестка не заметила",
               "Планёрка у руководителя: слушают семеро, в графике — один",
               "Совещание, которое могло быть письмом"],
    "SM-006": ["Включила камеру на созвоне раньше всех",
               "Вечерний концерт для подписчиков в количестве трёх",
               "Выступаю, а микрофон всё ещё на паузе"],
    "SM-007": ["Приехал на созвон красиво",
               "Единственное парковочное место — моё",
               "Когда взял выходной, а загород сам себя не покажет"],
    "SM-011": ["Стычка двух отделов за общий ресурс",
               "Когда обе стороны уверены, что правы",
               "Дедлайн общий. Аргументы — тоже"],
    "SM-012": ["Спустил задачу вниз. Лично",
               "Делегирование без лишних слов",
               "Таск-трекер уровня Хамзанамы"],
    "SM-013": ["Два тимлида. Один бюджет",
               "Слияние отделов идёт непросто",
               "Оба правы. Оба слоны"],
    "SM-014": ["Корпоратив года: явка обязательна",
               "Свадьба дочери начальника: весь двор пришёл",
               "Когда фуршет объявили в другом корпусе"],
    "SM-015": ["Пятница. Продакшен. Без плана отката",
               "Новый стажёр и база данных",
               "Кто-то снова задеплоил в пятницу"],
    "SM-016": ["Ответил всем сразу. Зря.",
               "Reply all на 400 человек",
               "Когда эскалировал — и прилетело всем"],
    "SM-017": ["Весь отдел вышел на один баг",
               "Охота на баг вышла на уровень эпохи",
               "Тестировщики выехали на прод"],
    "SM-018": ["Годовая стратегия: слушают семеро, решает один",
               "Совещание, которое могло быть письмом",
               "Объявил курс. Все кивнули"],
    "SM-019": ["Совещание у того, кто всё уже решил",
               "Планёрка без права на возражение… почти",
               "Совет директоров: слушают, кивают, не соглашаются"],
    "SM-020": ["Лучший консультант всё ещё в пещере",
               "Мудрость без созвона и слайдов",
               "Совет, который старше всех дедлайнов"],
}

TITLES = {
    "SM-001": "Битва при Ланке (Удайпур, 1649–53)",
    "SM-002": "Рама отпускает шпионов Шуку и Шарану (Манаку, серия «Осада Ланки»)",
    "SM-003": "Ибрахим, сын Хамзы, мчится в битву (Хамзанама Акбара, ок. 1570-е, Chester Beatty) — пере-источник SM-003 27-09-2026: прежний мастер 800×547 не тянул фрагмент",
    "SM-004": "Кумбхакарна повержен (Малва)",
    "SM-005": "Шах-Джахан на террасе (ок. 1627–28, MET)",
    "SM-006": "Дама с танпурой (ок. 1735, MET)",
    "SM-007": "Махарана Санграм Сингх на коне (ок. 1712, MET)",
    "SM-011": "Арджуна сражается с раджей Тамрадхваджей (Размнама, ок. 1616–17, MET)",
    "SM-012": "Умар пинает пехотинца у крепости Фулад (Хамзанама, Кесу Калан, ок. 1570, MET; рисунок тоном)",
    "SM-013": "Два слона бьются перед Мухаммад-шахом (Найнсукх, ок. 1730–40, Cleveland)",
    "SM-014": "Свадебная процессия Дары Шукоха (Хаджи Мадни, 1740-е)",
    "SM-015": "Акбар укрощает слона Хаваи (Басаван, ок. 1590)",
    "SM-016": "Ашваттхама обрушивает оружие Нараяны на пандавов (Размнама, ок. 1616–17, MET)",
    "SM-017": "Раджа Балвант Дев Сингх на тигриной охоте (Найнсукх, ок. 1750)",
    "SM-018": "Делийский дарбар Акбара II (Гулам Муртаза Хан, ок. 1811)",
    "SM-019": "Двор Раваны (Рамаяна, ок. 1605, MET)",
    "SM-020": "Царь Дабшалим у мудреца Бидпая (Калила и Димна, Абу-л Хасан, ок. 1610)",
}

SHEETS = {
    "batch1": {
        "ids": ["SM-00%d" % i for i in range(1, 8)],
        "sheet_id": "sufferingmahabharata-meme-batch1-fragments_27-09-2026",
        "title": "«Страдающая Бхарата» — партия 1, подтверждение ФРАГМЕНТОВ: 7 карт",
        "subtitle": "H5529 · 26-09 MG голосовал по мастерам; постится фрагмент (формат 27-09-2026) — "
                    "лист показывает то, что уйдёт в канал. SM-003 пере-источен (мастер 800×547 → Хамзанама, 3840×5716). "
                    "Подписи — утверждённые MG. Красные линии: только быт/двор/охота/битвы, без шуток над почитаемыми образами, "
                    "ноль постов до утверждения.",
        "note_SM-003": "<p><b>Пере-источник (H5529):</b> прежний мастер (800×547, «Битва из рукописи Рамаяны») не давал "
                       "фрагмента ≥500 px. Замена: Хамзанама Акбара, ок. 1570-е (Chester Beatty, Public domain, 3840×5716) — "
                       "та же сценика «все бьются со всеми», подпись MG сохранена. MG решает.</p>",
    },
    "batch2": {
        "ids": ["SM-0%02d" % i for i in range(11, 21)],
        "sheet_id": "sufferingmahabharata-meme-batch2-10_27-09-2026",
        "title": "«Страдающая Бхарата» — партия 2: 10 мемов на утверждение",
        "subtitle": "H5529 · микс быт/повестка/субхашита 7/2/1 · все карточки собраны сразу на фрагментах "
                    "(формат 27-09-2026), мастера ≥1500 px. Красные линии месяца 1: только быт/двор/охота/битвы, "
                    "без шуток над почитаемыми образами, ноль постов до утверждения. SM-012 — рисунок тоном "
                    "(монохром), вторичный формат жанра.",
        "note_SM-003": "",
    },
}


def main(party):
    cfg = SHEETS[party]
    tsv = os.path.join(REPO, "memes.tsv")
    with open(tsv, newline="", encoding="utf-8") as f:
        all_rows = list(csv.DictReader(f, delimiter="\t"))
    rows = [r for r in all_rows if r["id"] in cfg["ids"]]
    assert rows and len(rows) == len(cfg["ids"]), "реестр не совпадает с партией"
    assert len({r["id"] for r in rows}) == len(rows), "дубли в реестре"
    for r in rows:
        assert r["source_url"] and r["license"], r["id"]
        img = r.get("fragment_file") or r["file"]  # в лист идёт то, что постится
        assert os.path.exists(os.path.join(REPO, img)), img

    manifest = EvidenceManifest(cfg["sheet_id"], [r["id"] for r in rows], repo_root=REPO)
    manifest.declare_joined("memes.tsv", ["id", "file", "source_url", "license",
                                          "attribution", "caption", "humor_class"])

    items = []
    for r in rows:
        cid = r["id"]
        img = r.get("fragment_file") or r["file"]
        caps = CAPTIONS[cid]
        opts = "<ol>" + "".join(
            "<li><b>%s.</b> «%s»%s</li>" % ("АБВ"[i], c,
                                            " <i>(в memes.tsv как основная)</i>" if i == 0 else "")
            for i, c in enumerate(caps)) + "</ol>"
        note = cfg.get("note_SM-003", "") if cid == "SM-003" else ""
        if party == "batch2" and cid == "SM-019":
            note = ("<p><b>Красная линия:</b> сюжет — двор Раваны как «совещание»; шутка про процесс "
                    "(совещание/повестку), не про религиозное почитание. MG решает.</p>")
        q = ('<img src="%s%s" alt="%s" style="max-width:640px;max-height:520px;'
             'display:block;margin:6px auto;border:1px solid #ccc;background:#fff;">'
             '<p style="text-align:center"><b>%s</b> · источник: %s</p>'
             '<p style="text-align:center">Утвердить карточку? Выбранную подпись '
             'укажите в заметке: <b>А / Б / В</b> или свой вариант текста.</p>'
             % (RAW, img, TITLES[cid], TITLES[cid], r["attribution"]))
        items.append({
            "id": cid,
            "filt": r["humor_class"],
            "title": "%s — %s [%s]" % (cid, TITLES[cid], r["humor_class"]),
            "question": q + note,
            "panels": [
                ("Подписи на выбор", opts),
                ("Источник", "<p>%s<br>Лицензия: <b>%s</b><br>Атрибуция: %s</p>"
                 % (r["source_url"], r["license"], r["attribution"])),
            ],
        })
        manifest.add_card(cid, {"source_url": r["source_url"], "license": r["license"],
                                "attribution": r["attribution"], "file": r["file"]})
    if party == "batch1":
        manifest.declare_omitted_path(
            "RussianRamayana/Leitan-Sundarakanda/*_media (остальные 617 сканов)",
            "пул зарегистрирован в Uprava DATA_LAYERS_CENSUS.md; в пилот взяты 3 страницы "
            "с наиболее мем-способными стихами")

    config = {
        "sheet_id": cfg["sheet_id"],
        "title": cfg["title"],
        "subtitle": cfg["subtitle"],
        "footer": "Реестр: github.com/gasyoun/SufferingMahabharata (memes.tsv). "
                  "Постинг (t.me/samskrtamru + VK-зеркало, тег #индомемы, каденция 1 раз в 2 недели) "
                  "гейтится этим листом: approved → пост. Ноль постов без утверждения MG.",
        "approve_label": "Одобрить",
        "reject_label": "Забраковать",
        "filters": [("быт", "быт (70%)"), ("повестка", "повестка (20%)"),
                    ("субхашита", "субхашита (10%)")],
        "generated": "2026-09-27",
        # V13 (H2854): no bare internal id on a reviewer's plate — each SM-NNN
        # card names its real-world artwork identity in the question.
        "identity_gate": {
            "patterns": [r"SM-\d{3}"],
            "labels": {cid: TITLES[cid] for cid in TITLES},
        },
        # Имена собственные из URL первоисточников (Commons-файлы), не IAST-утечки:
        # шапки карточек и подписи — кириллица.
        "preflight": {
            "allow_slp1_tokens": ["Hamza", "Ibrahim", "Umar", "Fulad", "Balwant",
                                  "Dabshalim", "Bidpay", "Tamradhvaja", "Asvatthama",
                                  "Narayana"],
        },
    }
    screening = {
        "deterministic": len(rows), "lookup": 0, "agent": len(rows), "human": 0,
        "evidence_path": "memes.tsv",
        "rules": ["%d/%d: изображение валидно, source_url и license непусты" % (len(rows), len(rows)),
                  "%d/%d: класс юмора в {быт, повестка, субхашита}, микс 7/2/1" % (len(rows), len(rows)),
                  "%d/%d: источники только MET/Cleveland open access / Wikimedia / Chester Beatty (PD/CC0); "
                  "текстовые рукописные сканы исключены (рулинг MG 26-09)" % (len(rows), len(rows)),
                  "%d/%d: мастера ≥1500 px, фрагменты нарезаны crop_fragment.py без [warn]" % (len(rows), len(rows))],
    }
    html = render_review_sheet(items, config, screening=screening, manifest=manifest)
    out_path = os.path.join(REPO, "review", "%s_review.html" % cfg["sheet_id"])
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("written:", out_path, len(html), "bytes")
    manifest.write(out_path.replace(".html", "_manifest.json"))


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg not in SHEETS:
        raise SystemExit("usage: gen_pilot_sheet.py batch1|batch2")
    main(arg)
