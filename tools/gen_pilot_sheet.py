#!/usr/bin/env python3
"""Generate the MG approval sheet for the SufferingMahabharata pilot (10 meme cards).

Committed generator (the H2929 lesson): the hub copy at gasyoun.github.io/vote/sheets/
is archival; this script is the regen path. Emitter: csl-pyutil render_review_sheet.

Usage: python3 tools/gen_pilot_sheet.py [out.html]
"""
import csv
import os
import sys

from csl_pyutil.review_sheet import render_review_sheet
from csl_pyutil.evidence import EvidenceManifest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = "https://raw.githubusercontent.com/gasyoun/SufferingMahabharata/main/"

# 2–3 caption variants per card; variant А mirrors the primary caption in memes.tsv.
CAPTIONS = {
    "SM-001": ["Понедельник: все задачи в статусе «горит»",
               "Выкатили релиз в пятницу — разобрались к среде",
               "Когда пришёл на планёрку, а там уже все"],
    "SM-002": ["Отдел безопасности поймал двоих, кто пересылал мемы мимо рабочего чата",
               "Обнаружили двух коллег, которые все пять лет работали ни разу не написав в общий чат",
               "Спамеров нашли. Отпустили с почётом"],
    "SM-003": ["Когда вся компания бросила дела на один общий дедлайн",
               "Тимбилдинг прошёл активно",
               "Итоги квартала подводим все вместе"],
    "SM-004": ["Будильник прозвенел в 6:00. Кумбхакарна проиграл",
               "«Ещё пять минут» — год Five Minutes Later",
               "Разбудили — теперь весь квартал виноват"],
    "SM-005": ["Планёрка у руководителя: слушают семеро, в графике — один",
               "Совещание, которое могло быть письмом",
               "Утвердил повестку. Повестка не заметила"],
    "SM-006": ["Включила камеру на созвоне раньше всех",
               "Вечерний концерт для подписчиков в количестве трёх",
               "Выступаю, а микрофон всё ещё на паузе"],
    "SM-007": ["Единственное парковочное место — моё",
               "Приехал на созвон красиво",
               "Когда взял выходной, а загород сам себя не покажет"],
    "SM-008": ["Стратегическая сессия: план безупречен, дедлайн — вчера",
               "Написал план. План написал меня",
               "Чек-лист готов. Осталось найти исполнителя"],
    "SM-009": ["Личные границы: объявлены чётко, без переговоров",
               "Ответ «нет» — полное предложение",
               "Твёрдость без единого лишнего слова"],
    "SM-010": ["Упама уровня «дочь слона увидела льва» — курс санскрита сам себя не пройдёт",
               "Санскритская сравнительная степень: страшно, но изящно",
               "Для знатоков: классическая упама, издание 1888 года"],
}

TITLES = {
    "SM-001": "Битва при Ланке (Удайпур, 1649–53)",
    "SM-002": "Рама отпускает шпионов Шуку и Шарану (Манаку, серия «Осада Ланки»)",
    "SM-003": "Битва из рукописи Рамаяны",
    "SM-004": "Кумбхакарна повержен (Малва)",
    "SM-005": "Шах-Джахан на террасе (ок. 1627–28, MET)",
    "SM-006": "Дама с танпурой (ок. 1735, MET)",
    "SM-007": "Махарана Санграм Сингх на коне (ок. 1712, MET)",
    "SM-008": "Хануман строит план (Рамаяна V.30, скан издания 1888)",
    "SM-009": "Сита отвечает Раване (Рамаяна V.26, скан издания 1888)",
    "SM-010": "Упама «слониха и лев» (Рамаяна V.28, скан издания 1888)",
}


def main(out_path):
    tsv = os.path.join(REPO, "memes.tsv")
    with open(tsv, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    assert len(rows) == 10, "expected exactly 10 pilot rows, got %d" % len(rows)
    for r in rows:
        assert r["source_url"] and r["license"], r["id"]
        assert os.path.exists(os.path.join(REPO, r["file"])), r["file"]

    manifest = EvidenceManifest("suffering-mahabharata-pilot-10_26-09-2026",
                                [r["id"] for r in rows], repo_root=REPO)
    manifest.declare_joined("memes.tsv", ["id", "file", "source_url", "license",
                                          "attribution", "caption", "humor_class"])

    items = []
    for r in rows:
        cid = r["id"]
        caps = CAPTIONS[cid]
        opts = "<ol>" + "".join(
            "<li><b>%s.</b> «%s»%s</li>" % ("АБВ"[i], c,
                                            " <i>(в memes.tsv как основная)</i>" if i == 0 else "")
            for i, c in enumerate(caps)) + "</ol>"
        q = ('<img src="%s%s" alt="%s" style="max-width:640px;max-height:520px;'
             'display:block;margin:6px auto;border:1px solid #ccc;background:#fff;">'
             '<p style="text-align:center"><b>%s</b> · источник: %s</p>'
             '<p style="text-align:center">Утвердить карточку в пилот? Выбранную подпись '
             'укажите в заметке: <b>А / Б / В</b> или свой вариант текста.</p>'
             % (RAW, r["file"], TITLES[cid], TITLES[cid], r["attribution"]))
        note = ""
        if cid == "SM-009":
            note = ("<p><b>Красная линия:</b> подпись прославляющая (границы объявлены), "
                    "не насмешка — месяц 1 никаких шуток над почитаемыми образами. "
                    "MG решает.</p>")
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
    manifest.declare_omitted_path(
        "RussianRamayana/Leitan-Sundarakanda/*_media (остальные 617 сканов)",
        "пул зарегистрирован в Uprava DATA_LAYERS_CENSUS.md; в пилот взяты 3 страницы "
        "с наиболее мем-способными стихами")

    config = {
        "sheet_id": "suffering-mahabharata-pilot-10_26-09-2026",
        "title": "«Страдающая Махабхарата» — пилот: 10 мемов на утверждение",
        "subtitle": "H5507 · партия 1 · все карточки status=draft, ноль постов до утверждения · "
                    "красные линии месяца 1: только быт/двор/охота/битвы, без шуток над почитаемыми образами",
        "footer": "Реестр: github.com/gasyoun/SufferingMahabharata (memes.tsv). "
                  "Постинг (TG @strad_mahabharata + VK) гейтится этим листом: approved → пост.",
        "approve_label": "Одобрить",
        "reject_label": "Забраковать",
        "filters": [("быт", "быт (70%)"), ("повестка", "повестка (20%)"),
                    ("субхашита", "субхашита (10%)")],
        "generated": "2026-09-26",
        # V13 (H2854): no bare internal id on a reviewer's plate — each SM-NNN
        # card names its real-world artwork/verse identity in the question.
        "identity_gate": {
            "patterns": [r"SM-\d{3}"],
            "labels": {cid: TITLES[cid] for cid in TITLES},
        },
    }
    screening = {
        "deterministic": 10, "lookup": 0, "agent": 10, "human": 0,
        "evidence_path": "memes.tsv",
        "rules": ["10/10: изображение валидно, source_url и license непусты",
                  "10/10: класс юмора в {быт, повестка, субхашита}, микс 7/2/1",
                  "10/10: источники только MET open access / Wikimedia / локальные PD-сканы; "
                  "t.me/ramayanaru файловым источником не служил",
                  "10/10: отобрано вручную по красным линиям месяца 1 (быт/двор/битвы)"],
    }
    html = render_review_sheet(items, config, screening=screening, manifest=manifest)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("written:", out_path, len(html), "bytes")
    manifest.write(out_path.replace(".html", "_manifest.json"))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO, "review", "sufferingmahabharata-meme-pilot-10_26-09-2026_review.html"))
