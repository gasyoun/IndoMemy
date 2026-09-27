#!/usr/bin/env python3
"""Кроп-фрагмент для карточек «Страдающей Махабхараты» (рулинг MG 27-09-2026).

Жанр «Страдающее Средневековье» постит ФРАГМЕНТ детали (~600 px), не целый лист
и не целую страницу. Замер живого паблика 27-09-2026 (8 образцов): 6 квадратов
ar 0,97–1,11, длинная сторона ровно ~600 px; широкие образцы — тоже кропы
(лицо крупным планом), а не страницы.

Вход:  memes.tsv, колонка `fragment_box` = "cx,cy,frac"
       cx,cy — центр кропа в долях ширины/высоты мастера (0..1)
       frac  — сторона квадрата как доля МЕНЬШЕЙ стороны мастера (0..1)
Выход: images/fragments/<id>.jpg, длинная сторона <= --long (по умолчанию 640).
       Колонка `fragment_file` проставляется флагом --write-tsv.

  python3 tools/crop_fragment.py                 # все строки с fragment_box
  python3 tools/crop_fragment.py --id SM-002     # одна карта
  python3 tools/crop_fragment.py --sheet         # + контактный лист review/fragments_sheet.png
  python3 tools/crop_fragment.py --write-tsv     # проставить fragment_file в memes.tsv

Требуется Pillow. Мастер не портится: кроп — производный файл.
"""
import argparse
import csv
import os

from PIL import Image, ImageDraw

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TSV = os.path.join(REPO, "memes.tsv")
OUTDIR = os.path.join(REPO, "images", "fragments")
SHEET = os.path.join(REPO, "review", "fragments_sheet.png")
MIN_MASTER = 1500  # меньше — фрагмент выходит мылом; мастер надо пере-искать


def read_rows():
    with open(TSV, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


LANCZOS = Image.Resampling.LANCZOS


def parse_box(box):
    cx, cy, frac = (float(x) for x in box.split(","))
    return cx, cy, frac


def crop_square(im, box, long_edge):
    cx, cy, frac = parse_box(box)
    w, h = im.size
    side = max(64, int(round(frac * min(w, h))))
    x0 = int(round(cx * w - side / 2))
    y0 = int(round(cy * h - side / 2))
    xc, yc = x0, y0                       # запрошенный угол
    x0 = max(0, min(x0, w - side))        # clamp: угол внутри листа
    y0 = max(0, min(y0, h - side))
    clamped = abs(x0 - xc) > 2 or abs(y0 - yc) > 2   # >2 px — не округление, а сдвиг
    frag = im.crop((x0, y0, x0 + side, y0 + side))
    if frag.size[0] > long_edge:
        frag = frag.resize((long_edge, long_edge), LANCZOS)
    real_cx = (x0 + side / 2) / w
    real_cy = (y0 + side / 2) / h
    return frag, side, clamped, (real_cx, real_cy)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", help="только одна карточка")
    ap.add_argument("--long", type=int, default=640, help="макс. длинная сторона (жанр ~600)")
    ap.add_argument("--sheet", action="store_true", help="контактный лист для глазной проверки")
    ap.add_argument("--write-tsv", action="store_true", help="проставить fragment_file")
    args = ap.parse_args()

    rows = read_rows()
    os.makedirs(OUTDIR, exist_ok=True)
    done, warns = [], []
    for r in rows:
        cid = r["id"]
        if args.id and cid != args.id:
            continue
        if not (r.get("fragment_box") or "").strip():
            continue
        master = os.path.join(REPO, r["file"])
        if not os.path.exists(master):
            warns.append(f"{cid}: нет мастера {r['file']}")
            continue
        im = Image.open(master).convert("RGB")
        if max(im.size) < MIN_MASTER:
            warns.append(f"{cid}: мастер {im.size} < {MIN_MASTER} — фрагмент выйдет мягким, нужен пере-источник")
        frag, side, clamped, real = crop_square(im, r["fragment_box"], args.long)
        if clamped:
            cx, cy, _ = parse_box(r["fragment_box"])
            warns.append(f"{cid}: fragment_box вне диапазона — центр сдвинут "
                         f"({cx:.2f},{cy:.2f} → {real[0]:.2f},{real[1]:.2f}); "
                         f"уменьшите frac или сдвиньте cx,cy внутрь листа")
        if side < 500:
            warns.append(f"{cid}: фрагмент {side}px < 500 — жанровая норма ~600 px; "
                         f"мастер мелкий, нужен пере-источник")
        out = os.path.join("images", "fragments", f"{cid}.jpg")
        frag.save(os.path.join(REPO, out), quality=88, optimize=True)
        r["fragment_file"] = out
        done.append(f"{cid}: мастер {im.size} → фрагмент {side}px → {out}")
        print(f"[ok] {done[-1]}")

    if args.write_tsv and done:
        with open(TSV, encoding="utf-8", newline="") as f:
            rows_now = list(csv.DictReader(f, delimiter="\t"))
            fields = list(rows_now[0].keys())
        for r in rows_now:
            hit = next((d for d in done if d.startswith(r["id"] + ":")), None)
            if hit:
                r["fragment_file"] = os.path.join("images", "fragments", f"{r['id']}.jpg")
        with open(TSV, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields, delimiter="\t", lineterminator="\n")
            w.writeheader()
            w.writerows(rows_now)
        print(f"[ok] fragment_file проставлен в memes.tsv ({len(done)} строк)")

    if args.sheet and done:
        cell, cols = 420, 4
        picked = [r for r in rows if (r.get("fragment_box") or "").strip()]
        picked = [r for r in picked if os.path.exists(os.path.join(REPO, r["fragment_file"] or
                                                                   os.path.join("images", "fragments", r["id"] + ".jpg")))]
        rowsn = (len(picked) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * cell, rowsn * (cell + 26)), "white")
        dr = ImageDraw.Draw(sheet)
        for i, r in enumerate(picked):
            p = os.path.join(REPO, r["fragment_file"] or os.path.join("images", "fragments", r["id"] + ".jpg"))
            t = Image.open(p).convert("RGB").resize((cell, cell), Image.LANCZOS)
            x, y = (i % cols) * cell, (i // cols) * (cell + 26)
            sheet.paste(t, (x, y))
            dr.text((x + 6, y + cell + 5), f"{r['id']}  {r['caption'][:38]}", fill="black")
        os.makedirs(os.path.dirname(SHEET), exist_ok=True)
        sheet.save(SHEET)
        print(f"[ok] контактный лист: {os.path.relpath(SHEET, REPO)}")

    for wmsg in warns:
        print(f"[warn] {wmsg}")


if __name__ == "__main__":
    main()
