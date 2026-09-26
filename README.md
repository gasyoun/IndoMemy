# «Страдающая Махабхарата» (SufferingMahabharata)

_Создан: 26-09-2026 · Мем-паблик «Страдающее Средневековье на индийский лад» — реестр и конвейер._

Формула поста: старинное изображение + современная бытовая подпись; в каждом посте — строка
источника (музей/издание/лицензия). Цель — воронка и популяризация: смешно сначала, глубоко потом
(мягкая подводка к курсам, книге Рамаяны, лекциям). Каналы: Telegram [@strad_mahabharata] + VK-зеркало.

## Красные линии месяца 1

1. **Свободная зона — только быт**: дворцы, охота, сцены битв, придворные сцены.
2. **Никакой шутки над почитаемыми образами** — мурти, богини, медитация; божественная тема —
   после отдельного рулинга MG (калибровка аудитории).
3. **Ноль постов без утверждения MG** — каждая партия проходит лист утверждения
   (gasyoun.github.io/vote), только `status=approved` → пост.

## Источники (жёсткое правило)

- **Музеи open access** (MET, Smithsonian, LACMA, Cleveland), **Wikimedia Commons**,
  **локальные PD-сканы** (издание Параба 1888, Sundarakandam — сканы в
  [RussianRamayana/Leitan-Sundarakanda](https://github.com/gasyoun/RussianRamayana/tree/main/Leitan-Sundarakanda)).
- **t.me/ramayanaru — НЕ файловый источник** (канал-лид для находок; файл берём из первоисточника).
- У каждого мема в [memes.tsv](memes.tsv) непустые `source_url` и `license`.

## Реестр — memes.tsv

`id · file · source_url · license · attribution · caption · humor_class · status · posted_at · tg_msg_id`

- `humor_class`: `быт` (70%) / `повестка` (20%) / `субхашита` (10%)
- `status`: `draft` → `approved` (лист MG) → `posted`
- Партия 1 (пилот, H5507): SM-001…SM-010, все `draft`.

## Конвейер

агенты отбирают кандидатов и пишут подписи → лист утверждения MG (~10 мин/партия) →
`approved` → постинг (TG ядро, VK зеркало) → `posted_at`/`tg_msg_id` заполняются.

## Лист утверждения

Хаб: [gasyoun.github.io/vote/sheets/suffering-mahabharata-pilot-10_26-09-2026.html]
(https://gasyoun.github.io/vote/sheets/suffering-mahabharata-pilot-10_26-09-2026.html)
Реген: `python3 tools/gen_pilot_sheet.py` (эмиттер csl-pyutil; генератор коммитится, хаб-копия — архивная).

_Гасунс_
