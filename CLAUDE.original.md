# CLAUDE.md — jaskiniowiec

## README to artefakt produktu

README nie jest zwykłą dokumentacją. To front door produktu — tekst, który czytają osoby nietechniczne, żeby zdecydować, czy jaskiniowiec jest wart instalacji. Traktuj go z taką samą uwagą jak copy w interfejsie.

**Zasady przy każdej zmianie README:**

- Każde zdanie musi być czytelne dla osoby, która nigdy nie używała agenta AI do kodu. Jeśli piszesz „hook SessionStart wstrzykuje kontekst systemowy”, przełóż to na coś zrozumiałego dla zwykłego użytkownika.
- Przykłady Before/After mają zostać pierwszą rzeczą, którą widzi użytkownik. To cały pitch.
- Tabela instalacji musi być zawsze kompletna i poprawna. Jedna błędna komenda oznacza realnie straconego użytkownika.
- Macierz funkcji musi być zgodna z tym, co naprawdę robi kod. Jeśli coś dochodzi albo znika, aktualizuj tabelę.
- Zachowaj głos README. Top-level `README.md` zostaje po angielsku i zachowuje upstreamowy styl.
- Liczby benchmarków bierz z realnych uruchomień w `benchmarks/` i `evals/`. Nigdy ich nie wymyślaj ani nie zaokrąglaj bez podstaw.
- Gdy dodajesz nowego agenta do tabeli instalacji, dodaj też pasujący blok `<details>`.
- Przed każdą zmianą README zrób test czytelności: czy nietechniczna osoba zrozumie działanie i instalację w 60 sekund?

---

## Przegląd projektu

Jaskiniowiec to polskojęzyczny fork projektu caveman. Zmusza agentów kodujących AI do odpowiadania w skondensowanej polszczyźnie stylizowanej na „jaskiniową”, zwykle oszczędzając ~65–75% tokenów wyjściowych bez utraty technicznej treści. Repo dostarcza skille, reguły i dokumentację dla kilku agentów.

---

## Struktura plików i źródła prawdy

### Główne pliki źródłowe — edytuj tylko je

| Plik | Co kontroluje |
|------|----------------|
| `skills/jaskiniowiec/SKILL.md` | Zachowanie głównego trybu: poziomy intensywności, zasady, auto-jasność, trwałość. To jedyne źródło prawdy dla zachowania trybu. |
| `rules/jaskiniowiec-activate.md` | Treść reguły zawsze-włączonej aktywacji. Edytuj tutaj, nie w kopiach agent-specific. |
| `skills/jaskiniowiec-commit/SKILL.md` | Zachowanie wiadomości commitów. Niezależny skill. |
| `skills/jaskiniowiec-review/SKILL.md` | Zachowanie code review. Niezależny skill. |
| `skills/jaskiniowiec-help/SKILL.md` | Karta szybkiej pomocy. Jednorazowy widok, nie trwały tryb. |
| `jaskiniowiec-compress/SKILL.md` | Zachowanie skilla kompresji. |

### Pliki generowane / synchronizowane automatycznie — nie edytuj bezpośrednio

Część kopii dla konkretnych agentów i bundli jest nadpisywana przez CI albo inne procesy synchronizacji. Zmiany w tych miejscach mogą zostać utracone.

---

## Workflow synchronizacji CI

`.github/workflows/sync-skill.yml` uruchamia się po zmianach w głównych skillach i regułach.

Co robi:
1. Kopiuje główny `SKILL.md` do zależnych lokalizacji
2. Odtwarza artefakty dystrybucyjne skilli
3. Buduje pliki reguł dla różnych agentów z jednego źródła
4. Commituje wynik z `[skip ci]`, żeby uniknąć pętli

Po mergu PR-a pamiętaj, że bot CI może dodać własny commit synchronizacyjny.

---

## System hooków (Claude Code)

W `hooks/` są trzy hooki. Komunikują się przez plik-flagę aktywnego trybu.

W praktyce:
- hook startu sesji ustawia domyślny tryb i wstrzykuje zasady do kontekstu
- hook wysyłki promptu śledzi aktywację i utrzymuje styl między turami
- statusline pokazuje aktywny tryb

Hooki muszą cicho ignorować błędy systemu plików i nigdy nie mogą blokować startu sesji.

---

## System skilli

Skille to pliki Markdown z frontmatterem YAML używane przez system skilli/pluginów Claude Code i przez `npx skills` u innych agentów.

### Poziomy intensywności

Zdefiniowane w `skills/jaskiniowiec/SKILL.md`. W tym forku obowiązują tylko trzy poziomy: `lite`, `full` i `ultra`. Poziom trwa do zmiany albo końca sesji.

### Reguła auto-jasności

Jaskiniowiec przechodzi na zwykłą prozę przy ostrzeżeniach bezpieczeństwa, działaniach nieodwracalnych, wieloetapowych instrukcjach, ryzyku niejednoznaczności i wtedy, gdy użytkownik potrzebuje doprecyzowania. Po jasnym fragmencie wraca do stylu zwięzłego.

### jaskiniowiec-compress

Pod-skill w `jaskiniowiec-compress/SKILL.md`. Bierze ścieżkę pliku, kompresuje prozę do stylu jaskiniowca, zapisuje wynik do oryginalnej ścieżki i odkłada czytelny backup w `<filename>.original.md`. Walidacja pilnuje, by nagłówki, bloki kodu, URL-e, ścieżki i komendy zostały zachowane.

### jaskiniowiec-commit / jaskiniowiec-review

Niezależne skille z własnymi polami `name` i `description`, więc mogą ładować się osobno.

---

## Dystrybucja do agentów

Jak jaskiniowiec trafia do różnych agentów:

| Agent | Mechanizm | Autoaktywacja? |
|-------|-----------|----------------|
| Claude Code | Plugin, hooki i skille | Tak |
| Codex | Plugin i hooki repo | Tak, jeśli hooki są aktywne |
| Gemini CLI | Rozszerzenie z `GEMINI.md` | Tak |
| Cursor / Windsurf / Cline / Copilot | Reguły repo / instrukcje | Zależnie od integracji |
| Inni | `npx skills` | Zwykle nie |

Nie obiecuj always-on tam, gdzie integracja naprawdę go nie zapewnia.

---

## Evals

`evals/` ma trzyramienny harness:
- `__baseline__` — bez system promptu
- `__terse__` — krótka instrukcja zwięzłości
- `<skill>` — ta sama instrukcja plus zawartość `SKILL.md`

Uczciwa delta to **skill vs terse**, nie skill vs baseline. Inaczej mieszasz efekt skilla z samym poleceniem „pisz krótko”.

`llm_run.py` wywołuje `claude -p --system-prompt ...` dla każdej pary (prompt, ramię), zapisuje wynik do `evals/snapshots/results.json`. `measure.py` liczy tokeny offline przez tiktoken. Proporcje mają sens; wartości bezwzględne są przybliżone.

Aby dodać skill: dodaj `skills/<name>/SKILL.md`. Aby dodać prompt: dopisz linię do `evals/prompts/en.txt`.

---

## Benchmarki

`benchmarks/` przepuszcza prawdziwe prompty przez API Claude i zapisuje surowe liczby tokenów. Wyniki są wersjonowane jako JSON, a tabela w README ma wynikać z tych danych.

Odtworzenie: `uv run python benchmarks/run.py` (wymaga `ANTHROPIC_API_KEY` w `.env.local`).

---

## Kluczowe zasady dla agentów pracujących tutaj

- Edytuj `skills/jaskiniowiec/SKILL.md`, jeśli zmieniasz zachowanie trybu.
- Edytuj `rules/jaskiniowiec-activate.md`, jeśli zmieniasz regułę autoaktywacji.
- `README.md` jest najważniejszym plikiem produktowym, ale w tym zadaniu ma pozostać po angielsku.
- Liczby benchmarków i evali muszą być prawdziwe. Bez zgadywania.
- Hooki mają cicho znosić błędy systemu plików. Nie mogą psuć startu sesji.
- Dokumentacja w tym zakresie ma być po polsku, spójna brandingowo i bez wariantów Wenyan / chińskich.
- Upstream `caveman` wolno wskazywać tylko jako źródło inspiracji albo pochodzenia forka.
