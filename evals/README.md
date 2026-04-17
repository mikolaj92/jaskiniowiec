# Evals

Mierzy rzeczywistą kompresję tokenów dla skilli jaskiniowca, uruchamiając te same prompty w Claude Code w trzech warunkach i porównując liczbę tokenów w wygenerowanej odpowiedzi.

## Trzy ramiona testu

| Ramię | System prompt |
|-----|--------------|
| `__baseline__` | brak |
| `__terse__` | `Odpowiadaj zwięźle.` |
| `<skill>` | `Odpowiadaj zwięźle.\n\n{SKILL.md}` |

Uczciwa delta dla dowolnego skilla to **`<skill>` vs `__terse__`** — czyli ile sam skill dokłada ponad zwykłe polecenie „pisz krótko”. Porównywanie skilla do wariantu bez system promptu miesza wpływ skilla z ogólną zwięzłością; wcześniejsza wersja harnessu robiła właśnie to i dlatego zawyżała wyniki.

## Dlaczego tak

- **Prawdziwe wyjście LLM**, nie ręcznie pisane przykłady.
- **Ten sam Claude Code**, pod który celują skille — bez osobnego klucza API.
- **Snapshot w git**, więc uruchomienia CI są deterministyczne i darmowe, a każdą zmianę liczb da się zrecenzować jako diff.
- **Ramię kontrolne** oddziela wkład skilla od zwykłego efektu „pisz krótko”.

## Pliki

- `prompts/en.txt` — stała lista pytań developerskich, po jednym w linii.
- `llm_run.py` — uruchamia `claude -p --system-prompt …` dla każdej pary (prompt, ramię), zapisuje prawdziwe wyjście LLM do `snapshots/results.json` wraz z metadanymi (model, wersja CLI, czas generacji).
- `measure.py` — czyta snapshot, liczy tokeny przez tiktoken `o200k_base`, wypisuje tabelę Markdown z medianą / średnią / min / max / odchyleniem standardowym.
- `snapshots/results.json` — wersjonowane źródło prawdy, odświeżane tylko wtedy, gdy zmienia się `SKILL.md` albo prompty.

## Odśwież snapshot (wymaga zalogowanego CLI `claude`)

```bash
uv run python evals/llm_run.py
```

To wywołuje Claude raz dla każdego promptu × (N skilli + 2 ramiona kontrolne). Żeby było taniej, użyj mniejszego modelu:

```bash
JASKINIOWIEC_EVAL_MODEL=claude-haiku-4-5 uv run python evals/llm_run.py
```

## Odczytaj snapshot (bez LLM, bez API key, działa w CI)

```bash
uv run --with tiktoken python evals/measure.py
```

## Dodanie promptu

Dopisz linię do `prompts/en.txt`, potem odśwież snapshot.

## Dodanie skilla

Dodaj `skills/<name>/SKILL.md`, potem odśwież snapshot. `llm_run.py` automatycznie wykrywa każdy katalog ze skillem.

## Czego to NIE mierzy

- **Wierności** — czy skrócona odpowiedź zachowuje techniczną treść? Skill odpowiadający wszędzie `ok` wygrałby samą kompresją. W przyszłości można dodać ocenę osobnym modelem.
- **Opóźnienia ani kosztu** — poza zakresem. Skille dodają tokeny wejściowe przy każdym wywołaniu, więc oszczędność na wyjściu nie pokazuje całej ekonomii.
- **Zachowania między modelami** — mierzymy tylko model użyty do wygenerowania snapshotu.
- **Dokładnych tokenów Claude** — `tiktoken o200k_base` to BPE OpenAI, więc tylko przybliża tokenizer Claude. Proporcje między ramionami są sensowne; wartości bezwzględne są przybliżone.
- **Istotności statystycznej** — jedno uruchomienie na parę (prompt, ramię) przy domyślnej temperaturze. Kolumny min/max/stdev pomagają ocenić szum, ale to nie jest pełny eksperyment statystyczny.
