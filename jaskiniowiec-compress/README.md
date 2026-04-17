<p align="center">
  <img src="https://em-content.zobj.net/source/apple/391/rock_1faa8.png" width="80" />
</p>

<h1 align="center">jaskiniowiec-compress</h1>

<p align="center">
  <strong>zmniejsz plik pamięci. oszczędzaj tokeny w każdej sesji.</strong>
</p>

---

Skill dla Claude Code, który kompresuje pliki pamięci projektu (`CLAUDE.md`, todo, preferencje) do stylu jaskiniowca — tak, żeby każda sesja startowała z mniejszym kosztem tokenów.

Claude czyta `CLAUDE.md` przy starcie każdej sesji. Duży plik = większy koszt. Jaskiniowiec zmniejsza plik. Koszt spada przy każdym kolejnym uruchomieniu.

## Co robi

```
/jaskiniowiec:compress CLAUDE.md
```

```
CLAUDE.md          ← wersja skompresowana (Claude czyta to przy starcie)
CLAUDE.original.md ← czytelny backup do edycji przez człowieka
```

Oryginał nie ginie. Możesz czytać i edytować `.original.md`, a potem ponownie uruchomić skill, żeby zrobić nową kompresję.

## Benchmarki

Prawdziwe wyniki na prawdziwych plikach projektowych:

| Plik | Oryginał | Kompresja | Oszczędność |
|------|----------:|----------:|------------:|
| `claude-md-preferences.md` | 706 | 285 | **59.6%** |
| `project-notes.md` | 1145 | 535 | **53.3%** |
| `claude-md-project.md` | 1122 | 636 | **43.3%** |
| `todo-list.md` | 627 | 388 | **38.1%** |
| `mixed-with-code.md` | 888 | 560 | **36.9%** |
| **Średnio** | **898** | **481** | **46%** |

Wszystkie walidacje przeszły ✅ — nagłówki, bloki kodu, URL-e i ścieżki plików zostały zachowane dokładnie.

## Przed / Po

<table>
<tr>
<td width="50%">

### 📄 Oryginał (706 tokenów)

> "I strongly prefer TypeScript with strict mode enabled for all new code. Please don't use `any` type unless there's genuinely no way around it, and if you do, leave a comment explaining the reasoning. I find that taking the time to properly type things catches a lot of bugs before they ever make it to runtime."

</td>
<td width="50%">

### 🪨 Jaskiniowiec (285 tokenów)

> "Preferuj TypeScript strict mode zawsze. Bez `any`, chyba że naprawdę inaczej się nie da — wtedy dopisz komentarz dlaczego. Dobre typy wcześnie łapią błędy."

</td>
</tr>
</table>

**Te same instrukcje. O 60% mniej tokenów. W każdej. Jednej. Sesji.**

## Bezpieczeństwo

`jaskiniowiec-compress` dostaje w Snyk ocenę High Risk przez wzorce `subprocess` i I/O plików wykrywane statycznie. To fałszywy alarm — szczegóły są w [SECURITY.md](./SECURITY.md).

## Instalacja

Kompresja jest częścią rodziny skilli jaskiniowca. Użyj `/jaskiniowiec:compress` w środowisku, które ładuje ten skill.

Jeśli potrzebujesz lokalnych plików, skill leży w:

```bash
jaskiniowiec-compress/
```

**Wymagane:** Python 3.10+

## Użycie

```
/jaskiniowiec:compress <ścieżka>
```

Przykłady:
```
/jaskiniowiec:compress CLAUDE.md
/jaskiniowiec:compress docs/preferences.md
/jaskiniowiec:compress todos.md
```

### Jakie pliki działają

| Typ | Kompresować? |
|------|-------------|
| `.md`, `.txt`, `.rst` | ✅ Tak |
| Naturalny język bez rozszerzenia | ✅ Tak |
| `.py`, `.js`, `.ts`, `.json`, `.yaml` | ❌ Pomiń (kod / config) |
| `*.original.md` | ❌ Pomiń (backup) |

## Jak to działa

```
/jaskiniowiec:compress CLAUDE.md
        ↓
wykrycie typu pliku      (bez tokenów)
        ↓
Claude kompresuje        (tokeny — jedno wywołanie)
        ↓
walidacja wyniku         (bez tokenów)
  sprawdza: nagłówki, kod, URL-e, ścieżki, listy
        ↓
przy błędach: Claude poprawia tylko wskazane miejsca   (tokeny — poprawka punktowa)
  bez pełnej rekompresji
        ↓
max 2 ponowienia
        ↓
zapis kompresji → CLAUDE.md
zapis oryginału → CLAUDE.original.md
```

Tokeny zużywają tylko dwie rzeczy: początkowa kompresja i ewentualna poprawka po walidacji. Reszta dzieje się lokalnie w Pythonie.

## Co zostaje zachowane

Jaskiniowiec kompresuje język naturalny. Nie rusza:

- bloków kodu (` ``` ` fenced albo wciętych)
- inline code (`` `backtick content` ``)
- URL-i i linków
- ścieżek plików (`/src/components/...`)
- komend (`npm install`, `git commit`)
- terminów technicznych, nazw bibliotek i API
- nagłówków (dokładny tekst zostaje)
- tabel (struktura zostaje, kompresowany jest tekst w komórkach)
- dat, wersji i liczb

## Dlaczego to ma znaczenie

`CLAUDE.md` ładuje się przy **każdym starcie sesji**. Plik pamięci projektu o wielkości 1000 tokenów kosztuje tokeny za każdym otwarciem projektu. Po 100 sesjach to 100 000 tokenów narzutu za kontekst, który już raz napisałeś.

Jaskiniowiec ścina to średnio o ~46%. Te same instrukcje. Ta sama dokładność. Mniej marnowania.

```
┌────────────────────────────────────────────┐
│  OSZCZĘDNOŚĆ NA PLIK    █████       46%    │
│  SESJE, KTÓRE KORZYSTAJĄ ██████████ 100%   │
│  ZACHOWANA INFORMACJA   ██████████ 100%    │
│  CZAS USTAWIENIA        █            1x    │
└────────────────────────────────────────────┘
```

## Część rodziny jaskiniowca

To element polskojęzycznego forka inspirowanego [caveman](https://github.com/JuliusBrussee/caveman) — narzędzi do skracania komunikacji bez utraty technicznej treści.

- **jaskiniowiec** — sprawia, że agent *mówi* krócej
- **jaskiniowiec-compress** — sprawia, że agent *czyta* mniej
