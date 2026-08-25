---
name: jaskiniowiec-compress
description: >
  Kompresuje naturalnojęzykowe pliki pamięci (`CLAUDE.md`, todo, preferencje)
  do stylu jaskiniowca, żeby oszczędzać tokeny wejściowe. Zachowuje całą
  treść techniczną, kod, URL-e i strukturę.
  Wersja skompresowana nadpisuje oryginał. Czytelny backup trafia do
  FILE.original.md.
  Wyzwalacz: /jaskiniowiec-compress <ścieżka> albo „skompresuj plik pamięci”.
---

# Jaskiniowiec Compress

## Cel

Kompresuj pliki naturalnojęzykowe (`CLAUDE.md`, todo, preferencje) do stylu jaskiniowca, żeby zmniejszyć koszt tokenów wejściowych. Wersja skompresowana nadpisuje oryginał. Czytelny backup trafia do `<filename>.original.md`.

## Wyzwalacz

`/jaskiniowiec-compress <ścieżka>` albo prośba użytkownika o skompresowanie pliku pamięci.

## Proces

1. Skrypty kompresji leżą w `jaskiniowiec-compress/scripts/` obok tego `SKILL.md`. Jeśli ścieżka nie jest oczywista, wyszukaj `jaskiniowiec-compress/scripts/__main__.py`.

2. Uruchom:

cd jaskiniowiec-compress && python3 -m scripts <absolute_filepath>

3. CLI zrobi:
- wykrycie typu pliku (bez tokenów)
- wywołanie Claude do kompresji
- walidację wyniku (bez tokenów)
- jeśli są błędy: punktowe poprawki przez Claude, bez pełnej rekompresji
- maksymalnie 2 ponowienia
- jeśli dalej nie działa: zgłoszenie błędu użytkownikowi i pozostawienie oryginału bez zmian

4. Zwróć wynik użytkownikowi

## Zasady kompresji

### Usuń
- rodzajniki i zbędne wypełniacze
- grzecznościowe wstępy typu „jasne”, „oczywiście”, „polecam”
- asekurację typu „warto rozważyć”, „możesz ewentualnie”
- redundantne frazy: „in order to” → „to”, „make sure to” → „ensure”, „the reason is because” → „because”
- pusty łącznikowy szum typu „however”, „furthermore”, „additionally”

### Zachowaj DOKŁADNIE (nigdy nie zmieniaj)
- bloki kodu (fenced ``` i wcięte)
- inline code (`backtick content`)
- URL-e i linki
- ścieżki plików (`/src/components/...`, `./config.yaml`)
- komendy (`npm install`, `git commit`, `docker build`)
- terminy techniczne (nazwy bibliotek, API, protokołów, algorytmów)
- nazwy własne (projekty, osoby, firmy)
- daty, wersje, liczby
- zmienne środowiskowe (`$HOME`, `NODE_ENV`)

### Zachowaj strukturę
- wszystkie nagłówki Markdown (dokładny tekst nagłówka, kompresuj tylko treść pod nim)
- hierarchię list wypunktowanych
- listy numerowane
- tabele (kompresuj tekst w komórkach, zachowaj strukturę)
- frontmatter / nagłówki YAML w plikach Markdown

### Kompresuj tak
- używaj krótkich synonimów: „duży”, nie „rozbudowany”; „napraw”, nie „zaimplementuj rozwiązanie”
- urwane zdania są OK: „Uruchom testy przed commitem”, nie „Powinieneś zawsze uruchamiać testy przed commitowaniem”
- wytnij „powinieneś”, „pamiętaj, żeby”, „upewnij się, że” — po prostu podaj akcję
- scalaj powtarzające się punkty mówiące to samo
- jeśli kilka przykładów pokazuje ten sam wzorzec, zostaw jeden

ZASADA KRYTYCZNA:
Wszystko wewnątrz ``` ... ``` musi zostać skopiowane DOKŁADNIE.
Nie wolno:
- usuwać komentarzy
- zmieniać spacji
- przestawiać linii
- skracać komend
- upraszczać niczego

Inline code (`...`) też ma zostać DOKŁADNIE bez zmian.
Nie zmieniaj niczego w backtickach.

Jeśli plik zawiera bloki kodu:
- traktuj je jako regiony tylko do odczytu
- kompresuj tylko tekst poza nimi
- nie łącz sekcji ponad kodem

## Wzorzec

Oryginał:
> You should always make sure to run the test suite before pushing any changes to the main branch. This is important because it helps catch bugs early and prevents broken builds from being deployed to production.

Kompresja:
> Uruchom testy przed pushem na main. Wcześnie łapiesz błędy, nie wypychasz zepsutego buildu na produkcję.

Oryginał:
> The application uses a microservices architecture with the following components. The API gateway handles all incoming requests and routes them to the appropriate service. The authentication service is responsible for managing user sessions and JWT tokens.

Kompresja:
> Architektura mikroserwisowa. API gateway kieruje żądania do usług. Serwis auth zarządza sesjami użytkownika i tokenami JWT.

## Granice

- Kompresuj TYLKO pliki naturalnojęzykowe (`.md`, `.txt`, bez rozszerzenia)
- NIGDY nie zmieniaj: `.py`, `.js`, `.ts`, `.json`, `.yaml`, `.yml`, `.toml`, `.env`, `.lock`, `.css`, `.html`, `.xml`, `.sql`, `.sh`
- Jeśli plik miesza prozę i kod, kompresuj tylko sekcje prozatorskie
- Jeśli nie masz pewności, czy coś jest kodem czy prozą, zostaw bez zmian
- Oryginał zapisuj jako backup `FILE.original.md` przed nadpisaniem
- Nigdy nie kompresuj `FILE.original.md`
