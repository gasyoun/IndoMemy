#!/usr/bin/env python3
"""Волна-2 мем-ремейков «Страдающей Бхараты» (H7838): композиты, фрагменты,
голосовой щит по формуле recrop-8 (PIL 4×2, id+подпись, durable-копия в review/).

Досье: review/meme-remakes-wave2-decisions_08-11-2026.md (PR#18, verdicts MG 08-11).
Гейт: постинг запрещён (рулинг 27-09) — щит ждёт MG-голосования; очередь волны-1
(16 approved / 0 posted) не перебивается.

  python3 tools/gen_wave2_shield.py          # композиты + фрагменты + щит + doc
  python3 tools/gen_wave2_shield.py --no-shield   # только мастера/фрагменты

Все источники — PD/CC0 (Wikimedia Commons; MET/Cleveland open access). Композиты
(A1 Дрейк, A3 Expanding brain) собираются из кропов разных листов — производные
файлы, мастера-первоисточники лежат рядом (sm2_*). Подписи — вердикты досье.
"""
import argparse
import os

from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(REPO, "images")
FRAG = os.path.join(IMG, "fragments")
REVIEW = os.path.join(REPO, "review")
SHIELD = os.path.join(REVIEW, "meme-remakes-wave2_shield_27-11-2026.png")
PRODDOC = os.path.join(REVIEW, "meme-remakes-wave2-production_27-11-2026.md")
FONT = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"

# (master_file, cx, cy, frac) — cx,cy в долях мастера, frac — доля меньшей стороны.
# Порядок панелей A1: верх = «отвернулся», низ = «одобрил» (оба кропа — лист
# MET 55873, ДРУГОЙ лист серии, не 55120 из SM-012).
DRAKE_PANELS = [
    ("sm2_misbah_grocer.jpg", 0.36, 0.44, 0.20),
    ("sm2_misbah_grocer.jpg", 0.56, 0.47, 0.22),
]
# A3 Expanding brain, эскалация помпезности: Джахангир (tonal bust) → Шах-Джахан
# конный, лицо → тот же лист, конный во весь рост с ангелами → Акбар со львом и
# телёнком (ангелы несут корону). Косяк-компромисс 27-11: MET DT5167 не докачался
# (Wikimedia 429), панели 2–3 — с одного листа; при перекропе panel-2 пересаживается
# на DT5167. MG решает по щиту.
BRAIN_PANELS = [
    ("sm2_jahangir_profile.jpg", 0.55, 0.42, 0.34),
    ("sm2_shahjahan_horseback.jpg", 0.44, 0.44, 0.17),
    ("sm2_shahjahan_horseback.jpg", 0.46, 0.45, 0.42),
    ("sm2_akbar_lion_calf.jpg", 0.45, 0.42, 0.26),
]

CAPTIONS = {
    "SM-021": "Выучить все формы „идти“. Встретить форму „идти“ — и не узнать её.",
    "SM-022": "Кнопки: «Выучить аорист» и «Выучить перфект». Осталось: обе.",
    "SM-023": "Знает слово dharma → знает семь значений dharma → знает, что dharma "
              "не переводится → сорок минут объясняет, почему.",
    "SM-024": "Применил все правила сандхи — получил ровно то, что в учебнике.",
    "SM-025": "Снег и любовь — один корень: snéha «липкость, привязанность» и наш "
              "«снег». Любовь липнет — проверено.",
    "SM-026": "Наш «огонь» и agníḥ — прямые родственники: слово старше алфавита, "
              "которым записано.",
    "SM-027": "mātṛ́, bhrā́tṛ, nakta: мать, брат, ночь — написано санскритологом, "
              "понятно бабушке.",
    "SM-028": "«Мёд» и madhu, «два» и dvā́ — считать до двух и до мёда мы умеем "
              "уже шесть тысяч лет.",
}

ORDER = ["SM-021", "SM-022", "SM-023", "SM-024", "SM-025", "SM-026", "SM-027", "SM-028"]


def crop_sq(path, cx, cy, frac):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    side = max(64, int(round(frac * min(w, h))))
    x0 = max(0, min(int(round(cx * w - side / 2)), w - side))
    y0 = max(0, min(int(round(cy * h - side / 2)), h - side))
    return im.crop((x0, y0, x0 + side, y0 + side))


def build_drake():
    panels = [crop_sq(os.path.join(IMG, f), cx, cy, fr) for f, cx, cy, fr in DRAKE_PANELS]
    side = min(p.size[0] for p in panels)
    panels = [p.resize((side, side), Image.LANCZOS) for p in panels]
    comp = Image.new("RGB", (side, side * len(panels)), "white")
    for i, p in enumerate(panels):
        comp.paste(p, (0, i * side))
    out = os.path.join(IMG, "sm2_drake_hamzanama.jpg")
    comp.save(out, quality=90)
    print("[ok] композит Дрейка:", out, comp.size)
    return out


def build_brain():
    panels = [crop_sq(os.path.join(IMG, f), cx, cy, fr) for f, cx, cy, fr in BRAIN_PANELS]
    side = min(p.size[0] for p in panels)
    panels = [p.resize((side, side), Image.LANCZOS) for p in panels]
    comp = Image.new("RGB", (side * 2, side * 2), "white")
    for i, p in enumerate(panels):  # TL → TR → BL → BR
        comp.paste(p, ((i % 2) * side, (i // 2) * side))
    out = os.path.join(IMG, "sm2_expanding_brain_dharma.jpg")
    comp.save(out, quality=90)
    print("[ok] композит Expanding brain:", out, comp.size)
    return out


def build_fragment(src, out_name, long_edge=640):
    im = Image.open(src).convert("RGB")
    if max(im.size) > long_edge:
        k = long_edge / max(im.size)
        im = im.resize((int(im.size[0] * k), int(im.size[1] * k)), Image.LANCZOS)
    out = os.path.join(FRAG, out_name)
    im.save(out, quality=88, optimize=True)
    print("[ok] фрагмент:", out, im.size)


def crop_fragment_single(cid, master_rel, box):
    """Кроп одной одиночной карты — та же математика, что tools/crop_fragment.py."""
    import csv
    path = os.path.join(REPO, master_rel)
    with open(os.path.join(REPO, "memes.tsv"), encoding="utf-8") as fh:
        pass  # boxes приходят аргументом; TSV тут не читается, чтобы не гонять csv
    cx, cy, frac = (float(x) for x in box.split(","))
    frag = crop_sq(path, cx, cy, frac)
    if max(frag.size) > 640:
        k = 640 / max(frag.size)
        frag = frag.resize((int(frag.size[0] * k), int(frag.size[1] * k)), Image.LANCZOS)
    out = os.path.join(FRAG, f"{cid}.jpg")
    frag.save(out, quality=88, optimize=True)
    print("[ok] фрагмент:", out, frag.size)


def wrap(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines[:2]


def build_shield(frag_by_id):
    cell, cols = 420, 4
    cap_h, head_h = 74, 46
    rows = 2
    W, H = cols * cell, head_h + rows * (cell + cap_h)
    sheet = Image.new("RGB", (W, H), "white")
    dr = ImageDraw.Draw(sheet)
    f_head = ImageFont.truetype(FONT, 20)
    f_id = ImageFont.truetype(FONT, 17)
    f_cap = ImageFont.truetype(FONT, 15)
    dr.rectangle([0, 0, W, head_h], fill=(240, 236, 228))
    dr.text((14, 12), "«Страдающая Бхарата» — волна-2: 8 мем-ремейков, щит для MG-голосования "
                      "(рулинг 27-09: постинг запрещён до явного шага MG)",
            fill="black", font=f_head)
    for i, cid in enumerate(ORDER):
        x, y = (i % cols) * cell, head_h + (i // cols) * (cell + cap_h)
        t = Image.open(frag_by_id[cid]).convert("RGB")
        k = min(cell / t.size[0], cell / t.size[1])
        t = t.resize((int(t.size[0] * k), int(t.size[1] * k)), Image.LANCZOS)
        sheet.paste(t, (x + (cell - t.size[0]) // 2, y + (cell - t.size[1]) // 2))
        dr.rectangle([x, y, x + cell, y + cell], outline=(200, 195, 185))
        dr.text((x + 8, y + cell + 6), cid, fill="black", font=f_id)
        lines = wrap(dr, CAPTIONS[cid], f_cap, cell - 16)
        for j, ln in enumerate(lines):
            dr.text((x + 8, y + cell + 26 + j * 20), ln, fill=(30, 30, 30), font=f_cap)
    sheet.save(SHIELD)
    print("[ok] щит:", SHIELD, sheet.size)


PROD_MD = """_Created: 27-11-2026 · Last updated: 27-11-2026_

# Волна-2 мем-ремейков — производство (H7838)

Досье-гейт: [meme-remakes-wave2-decisions_08-11-2026.md](https://github.com/gasyoun/IndoMemy/blob/main/review/meme-remakes-wave2-decisions_08-11-2026.md)
(PR#18). Щит: [meme-remakes-wave2_shield_27-11-2026.png](https://github.com/gasyoun/IndoMemy/blob/main/review/meme-remakes-wave2_shield_27-11-2026.png)
(формула recrop-8: PIL 4×2, id+подпись). **Постинг запрещён (рулинг 27-09)** —
щит ждёт MG-голосования; очередь волны-1 (16 approved / 0 posted) не перебивается.

| id | концепт | мастер(а) | источник(и) | лицензия | фрагмент |
|----|---------|-----------|-------------|----------|----------|
{rows}

## Замечания для MG

- **A1 (SM-021):** обе панели — с ОДНОГО другого листа серии MET 55873 (SM-012 = MET 55120 не клонировался);
  в досье стояло «другие листы» (мн.) — если нужен второй лист, панель «одобрил» пересаживается на
  MET 55118 при перекропе (закачка не удалась 27-11: Wikimedia 429).
- **A3 (SM-023):** эскалация помпезности: Джахангир (131499) → Шах-Джахан конный, лицо → конный во весь
  рост с ангелами (30663, два кропа одного листа) → Акбар со львом и телёнком (Говардхан, ангелы несут
  корону). Кандидат замены panel-2 — «Шах-Джахан на террасе» MET DT5167 (не докачался, 429). Композит
  2×2; при постинге пересобирается вертикально с текстом панелей — это черновик-щит.
- **A4 (SM-024):** «удивлённое лицо» — самое слабое воплощение партии: профиль брахмана с воздетыми
  руками (сцена «спрашивают брахмана»). MG решает; кандидат на замену — фигуры из MET 55118.
- **B1 (SM-025):** в доступных PD/CC0 (Wikimedia/MET/Cleveland) снежных миниатюр не нашлось (4 поисковых
  волны, дата 27-11-2026) — взят горный пейзаж Ramayana (MET 37.955): направление досье
  «гималайская зима/горы в миниатюре» в чтении «горы».
- **B3 (SM-027):** nakta=«ночь» воплощён дословно — ночная сцена семьи на Кайласе со звёздным небом
  (шутка про лексему, не про почитаемых — красная линия соблюдена).
- **B4 (SM-028):** «пир/угощение» — досье само оставляло арт «подбирается при производстве»: взят кроп
  подноса угощения из MET 55873 (тот же лист, что панели A1 — помечено; кандидат замены —
  «Джахангир и Хуррам на пиру у Нур-Джахан», PD, не докачался 429).
- **Дефект-класс 27-11-2026:** Wikimedia upload CDN устойчиво 429 c ~16:50 MSK; все мастера волны —
  ранее закачанные до блока 2000px-тумбы (≥1500 px, правило мастеров соблюдено).

_к.ф.н. М.Ю. Гасунс_
"""

ROWS_MD = {
    "SM-021": ("Дрейк, версия Хамзанамы (2 панели)", "sm2_misbah_grocer.jpg",
               'https://commons.wikimedia.org/wiki/File:"Misbah_the_Grocer_Brings_the_Spy_Parran_to_his_House",_Folio_from_a_Hamzanama_(The_Adventures_of_Hamza)_MET_55873.jpg',
               "CC0 (Met Open Access)",
               "«Мисбах-бакалейщик приводит шпиона Паррана к себе домой», Хамзанама, MET 55873 (обе панели — кропы одного листа)"),
    "SM-022": ("Two Buttons, дарбар", "sm2_sansar_chand_durbar.png",
               "https://commons.wikimedia.org/wiki/File:Painting_of_Raja_Sansar_Chand_of_Kangra_State_in_durbar_with_other_hill_rajas,_attributed_to_Purkhu,_Kangra,_ca.1803.png",
               "Public domain",
               "Раджа Сансар Чанд в дарбаре с горными раджа-соседями, приписывается Пуркху, Кангрa, ок. 1803"),
    "SM-023": ("Expanding brain, 4 портрета MET", "sm2_expanding_brain_dharma.jpg",
               "https://commons.wikimedia.org/wiki/File:Govardhan._Akbar_With_Lion_and_Calf_ca._1630,_Metmuseum.jpg",
               "Public domain / CC0 (Met Open Access)",
               "Портреты MET CC0: Джахангир (131499) → Шах-Джахан конный, лицо и во весь рост (30663) → Акбар со львом и телёнком (Говардхан, ок. 1630); композит 2×2; DT5167 — кандидат замены panel-2 (429 27-11)"),
    "SM-024": ("Surprised Pikachu, брахман", "sm2_brahman_tutinama.jpg",
               "https://commons.wikimedia.org/wiki/File:India,_Mughal,_Reign_of_Akbar,_16th_century_-_Page_from_Tales_of_a_Parrot_(Tuti-nama)-_Eleventh_night-_The_Brahman_is_ask_-_1962.279.89.a_-_Cleveland_Museum_of_Art.jpg",
               "CC0 (Cleveland Museum of Art)",
               "«Одиннадцатая ночь: спрашивают брахмана», Тутинама, Акбар, XVI в., Cleveland 1962.279.89.a"),
    "SM-025": ("снег ↔ snéha: горы в миниатюре", "sm2_hermitage_mountains.jpg",
               "https://commons.wikimedia.org/wiki/File:Rama,_Sita,_and_Lakshmana_at_the_Hermitage_of_Bharadvaja-_Folio_from_a_Ramayana_Series_(IA_mma_rama_sita_and_lakshmana_at_the_hermitage_of_bharadvaja_folio_from_a_ramay_37955).jpg",
               "Public domain (Met Open Access)",
               "«Рама, Сита и Лакшмана в ашраме Бхарадваджи», серия Рамаяны, MET 37.955 — кроп горного пейзажа"),
    "SM-026": ("огонь ↔ agníḥ: бытовой очаг", "sm2_bihzad_camp.jpg",
               "https://commons.wikimedia.org/wiki/File:Clevelandart_1944.490.a.jpg",
               "CC0 (Cleveland Museum of Art)",
               "Бехзад: «Музыканты и слуги у царского лагеря», Cleveland 1944.490.a — кроп сцены готовки у жаровни"),
    "SM-027": ("мать/брат/ночь: ночная семья", "sm2_kailash_night.jpg",
               "https://commons.wikimedia.org/wiki/File:Shiva_and_His_Family_on_Mount_Kailash.jpg",
               "Public domain",
               "«Шива и его семья на Кайласе», ночная сцена со звёздным небом — кроп семейной группы"),
    "SM-028": ("мёд ↔ mádhu, два ↔ dvā́: угощение", "sm2_misbah_grocer.jpg",
               'https://commons.wikimedia.org/wiki/File:"Misbah_the_Grocer_Brings_the_Spy_Parran_to_his_House",_Folio_from_a_Hamzanama_(The_Adventures_of_Hamza)_MET_55873.jpg',
               "CC0 (Met Open Access)",
               "«Мисбах-бакалейщик приводит шпиона Паррана к себе домой», MET 55873 — кроп сцены подноса угощения (слуги с блюдами); лист использован также SM-021, при перекропе заменяется на «Джахангир и Хуррам на пиру у Нур-Джахан» (PD, Google Art Project)"),
}


def write_prod_doc():
    lines = []
    for cid in ORDER:
        _, master, url, lic, attr = ROWS_MD[cid]
        lines.append("| %s | %s | `images/%s` | [%s](%s) | %s | `images/fragments/%s.jpg` |"
                     % (cid, ROWS_MD[cid][0], master, master, url, lic, cid))
    with open(PRODDOC, "w", encoding="utf-8") as f:
        f.write(PROD_MD.format(rows="\n".join(lines)))
    print("[ok] production-doc:", PRODDOC)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-shield", action="store_true")
    args = ap.parse_args()
    os.makedirs(FRAG, exist_ok=True)
    os.makedirs(REVIEW, exist_ok=True)

    drake = build_drake()
    brain = build_brain()
    build_fragment(drake, "SM-021.jpg")
    build_fragment(brain, "SM-023.jpg")

    singles = {
        "SM-022": ("sm2_sansar_chand_durbar.png", "0.46,0.38,0.42"),
        "SM-024": ("sm2_brahman_tutinama.jpg", "0.72,0.48,0.28"),
        "SM-025": ("sm2_hermitage_mountains.jpg", "0.33,0.28,0.45"),
        "SM-026": ("sm2_bihzad_camp.jpg", "0.24,0.81,0.18"),
        "SM-027": ("sm2_kailash_night.jpg", "0.45,0.52,0.42"),
        "SM-028": ("sm2_misbah_grocer.jpg", "0.42,0.72,0.24"),
    }
    for cid, (master, box) in singles.items():
        crop_fragment_single(cid, "images/" + master, box)

    write_prod_doc()
    if not args.no_shield:
        frag_by_id = {cid: os.path.join(FRAG, f"{cid}.jpg") for cid in ORDER}
        build_shield(frag_by_id)


if __name__ == "__main__":
    main()
