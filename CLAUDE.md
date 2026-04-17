# CLAUDE.md — jaskiniowiec

## README to artefakt produktu

README to nie zwykła dokumentacja. To wejście do produktu — tekst, który czytają osoby nietechniczne, żeby zdecydować, czy jaskiniowiec jest wart instalacji. Traktuj go jak copy interfejsu.

**Zasady przy każdej zmianie README:**

- Każde zdanie ma być czytelne dla osoby, która nigdy nie używała agenta AI do kodu. Jeśli piszesz „hook SessionStart wstrzykuje kontekst systemowy”, przełóż to na język zrozumiały dla użytkownika.
- Przykłady Before/After mają zostać na samym początku. To cały pitch.
- Tabela instalacji musi być zawsze pełna i poprawna. Jedna błędna komenda kosztuje realnego użytkownika.
- Tabela funkcji („What You Get”) musi zgadzać się z rzeczywistym działaniem kodu. Jeśli coś dochodzi albo znika, tabela też ma się zmienić.
- Zachowaj głos README. Top-level `README.md` zostaje po angielsku i zachowuje upstreamowy ton. Nie normalizuj go.
- Liczby benchmarków muszą pochodzić z realnych uruchomień w `benchmarks/` i `evals/`. Nigdy ich nie wymyślaj ani nie zaokrąglaj „na oko”.
- Gdy dodajesz nowego agenta do tabeli instalacji, dodaj też odpowiadający mu blok `<details>` poniżej.
- Przed każdą zmianą README zrób test czytelności: czy osoba nietechniczna zrozumie, co to robi i jak to zainstalować w 60 sekund?

---

## Przegląd projektu

Jaskiniowiec to polskojęzyczny fork upstreamowego projektu caveman. Sprawia, że agenci kodujący AI odpowiadają w skondensowanej, „jaskiniowej” polszczyźnie — zwykle oszczędzając ~65–75% tokenów wyjściowych bez utraty technicznej precyzji. Repo zawiera skille dla Claude Code, Codex i Gemini CLI oraz pliki reguł dla innych agentów.

---

## Struktura plików i źródła prawdy

### Główne pliki źródłowe — edytuj tylko je

| Plik | Co kontroluje |
|------|----------------|
| `skills/jaskiniowiec/SKILL.md` | Zachowanie trybu jaskiniowca: poziomy intensywności, zasady, auto-jasność, trwałość. To jedyny plik do zmian zachowania głównego trybu. |
| `rules/jaskiniowiec-activate.md` | Treść reguły zawsze-włączonej aktywacji. To źródło dla kopii specyficznych dla agentów. |
| `skills/jaskiniowiec-commit/SKILL.md` | Zachowanie skilla do wiadomości commitów. Niezależny skill. |
| `skills/jaskiniowiec-review/SKILL.md` | Zachowanie skilla do code review. Niezależny skill. |
| `skills/jaskiniowiec-help/SKILL.md` | Karta szybkiej pomocy. Jednorazowy widok, nie trwały tryb. |
| `jaskiniowiec-compress/SKILL.md` | Zachowanie skilla kompresji. |
| `skills/compress/SKILL.md` | Wewnętrzna kopia / wariant skilla kompresji używany przez system skilli. |

### Kopie generowane / synchronizowane automatycznie — nie edytuj bezpośrednio

Część plików specyficznych dla agentów i bundli jest nadpisywana przez CI lub inne mechanizmy synchronizacji. Jeśli edytujesz kopię zamiast źródła, zmiany mogą zniknąć.

---

## Synchronizacja CI

Workflow `.github/workflows/sync-skill.yml` synchronizuje pliki źródłowe po zmianach w głównych skillach i regułach.

Co robi:
1. Kopiuje główny `SKILL.md` do zależnych lokalizacji dla agentów
2. Odtwarza archiwum skilli używane przez część integracji
3. Buduje pliki reguł dla poszczególnych agentów z jednego źródła
4. Commituje wynik z `[skip ci]`, żeby nie zapętlać pipeline’u

Po mergu PR-a uwzględnij, że bot CI może dopisać własny commit synchronizacyjny.

---

## System hooków (Claude Code)

W `hooks/` są trzy hooki oraz moduł współdzielony. Komunikują się przez plik-flagę aktywnego trybu. Hooki mają działać cicho i nigdy nie mogą zablokować startu sesji przez błąd systemu plików.

W praktyce:
- hook startu sesji ustawia domyślny tryb i wstrzykuje zasady do kontekstu
- hook wysyłki promptu śledzi zmianę trybu i wzmacnia styl między turami
- skrypt statusline pokazuje aktywny tryb na pasku stanu

W dokumentacji technicznej zachowuj prawdziwe szczegóły implementacyjne, ale opisuj je po ludzku.

---

## System skilli

Skille to pliki Markdown z frontmatterem YAML, używane przez system pluginów Claude Code i przez `npx skills` u innych agentów.

### Poziomy intensywności

Zdefiniowane w `skills/jaskiniowiec/SKILL.md`. W tej gałęzi zostają tylko trzy poziomy: `lite`, `full` (domyślny) i `ultra`. Poziom trwa do zmiany albo końca sesji.

### Reguła auto-jasności

Jaskiniowiec automatycznie wraca do zwykłej prozy przy: ostrzeżeniach bezpieczeństwa, potwierdzeniach działań nieodwracalnych, wieloetapowych instrukcjach, gdy skrót mógłby wprowadzić błąd, oraz gdy użytkownik jest zagubiony albo powtarza pytanie. Po jasnym fragmencie wraca do stylu zwięzłego.

### jaskiniowiec-compress

Pod-skill w `jaskiniowiec-compress/SKILL.md`. Bierze ścieżkę do pliku, kompresuje prozę do stylu jaskiniowca, zapisuje wynik do oryginalnej ścieżki i tworzy backup w `<filename>.original.md`. Waliduje zachowanie nagłówków, bloków kodu, URL-i, ścieżek plików i komend. Przy błędzie robi maksymalnie 2 punktowe poprawki. Wymaga Pythona 3.10+.

### jaskiniowiec-commit / jaskiniowiec-review / jaskiniowiec-help

To niezależne skille z własnymi polami `name` i `description` w frontmatterze, dzięki czemu mogą ładować się osobno.

---

## Dystrybucja do agentów

Jaskiniowiec trafia do różnych agentów kilkoma drogami:

| Agent | Mechanizm | Autoaktywacja? |
|-------|-----------|----------------|
| Claude Code | Plugin / hooki / skille | Tak |
| Codex | Plugin + repozytoryjne hooki | Tak w repo, jeśli hooki są włączone |
| Gemini CLI | Rozszerzenie z `GEMINI.md` | Tak |
| Cursor / Windsurf / Cline / Copilot | Reguły repo lub instrukcje | Zależnie od integracji |
| Inni | `npx skills` | Zwykle nie — użytkownik uruchamia ręcznie |

Jeśli opisujesz integrację bez systemu hooków, nie obiecuj autoaktywacji, jeśli repo jej faktycznie nie zapewnia.

---

## Evals

`evals/` ma harness trzyramienny:
- `__baseline__` — bez system promptu
- `__terse__` — krótka ogólna instrukcja zwięzłości
- `<skill>` — ta sama instrukcja plus treść `SKILL.md`

Uczciwe porównanie to **skill vs terse**, nie skill vs baseline. Inaczej mieszasz efekt samej zwięzłości z efektem konkretnego skilla.

`llm_run.py` wywołuje `claude -p --system-prompt ...` dla każdej pary (prompt, ramię), zapisuje wynik do `evals/snapshots/results.json`. `measure.py` czyta snapshot offline i liczy tokeny przez tiktoken. Proporcje są istotniejsze niż absolutna liczba tokenów.

Aby dodać skill: dodaj `skills/<name>/SKILL.md`. Aby dodać prompt: dopisz linię do `evals/prompts/en.txt`.

---

## Benchmarki

`benchmarks/` przepuszcza prawdziwe prompty przez API Claude i zapisuje surowe liczby tokenów. Wyniki są wersjonowane jako JSON, a tabela w README powinna być aktualizowana tylko na podstawie tych wyników.

Odtworzenie: `uv run python benchmarks/run.py` (wymaga `ANTHROPIC_API_KEY` w `.env.local`).

---

## Kluczowe zasady dla agentów pracujących w tym repo

- Zmiany zachowania głównego trybu rób w `skills/jaskiniowiec/SKILL.md`. Nie edytuj kopii synchronizowanych.
- Zmiany reguły autoaktywacji rób w `rules/jaskiniowiec-activate.md`.
- `README.md` jest najważniejszym plikiem produktowym, ale zgodnie z zakresem tego forka pozostaje po angielsku.
- Liczby benchmarków i evali muszą być realne. Zero wymyślania.
- Hooki mają cicho znosić błędy systemu plików. Nie mogą rozwalić startu sesji.
- Dokumentacja w tym zakresie ma być po polsku, spójna brandingowo i bez wariantów Wenyan / chińskich.
- Upstream `caveman` można wspominać wyłącznie jako inspirację albo źródło pochodzenia forka, nie jako główny branding tej gałęzi.
