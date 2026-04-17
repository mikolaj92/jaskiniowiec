---
name: jaskiniowiec-commit
description: >
  Generator ultra-zwięzłych wiadomości commitów. Wycina szum, ale zachowuje
  intencję i uzasadnienie. Format Conventional Commits. Temat ≤50 znaków,
  treść tylko wtedy, gdy „dlaczego” nie jest oczywiste.
  Użyj, gdy użytkownik mówi „napisz commit”, „wiadomość commita”,
  „wygeneruj commit” albo wywołuje /jaskiniowiec-commit.
  Włącza się też przy pracy nad stagingiem zmian.
---

Pisz wiadomości commitów krótko i precyzyjnie. Conventional Commits. Bez waty. Ważniejsze „dlaczego” niż „co”.

## Zasady

**Linia tematu:**
- `<type>(<scope>): <imperative summary>` — `<scope>` opcjonalne
- Typy: `feat`, `fix`, `refactor`, `perf`, `docs`, `test`, `chore`, `build`, `ci`, `style`, `revert`
- Tryb rozkazujący: „add”, „fix”, „remove” — nie „added”, „adds”, „adding”
- ≤50 znaków, jeśli się da; twardy limit 72
- Bez kropki na końcu
- Dopasuj kapitalizację po dwukropku do konwencji projektu

**Treść (tylko gdy potrzebna):**
- Pomiń całkowicie, gdy temat sam wystarcza
- Dodaj tylko dla: nieoczywistego *dlaczego*, breaking changes, migracji, podlinkowanych issue
- Zawijaj do 72 znaków
- Używaj punktorów `-`, nie `*`
- Referencje do issue/PR na końcu: `Closes #42`, `Refs #17`

**Czego NIGDY nie dodawać:**
- „This commit does X”, „I”, „we”, „now”, „currently” — diff już pokazuje co
- „As requested by...” — użyj stopki `Co-authored-by`
- „Generated with Claude Code” ani żadnej atrybucji AI
- Emoji, chyba że projekt tego wymaga
- Powtarzania nazwy pliku, jeśli scope już to mówi

## Przykłady

Diff: nowy endpoint profilu użytkownika z treścią wyjaśniającą dlaczego
- ❌ "feat: add a new endpoint to get user profile information from the database"
- ✅
  ```
  feat(api): add GET /users/:id/profile

  Mobile client needs profile data without the full user payload
  to reduce LTE bandwidth on cold-launch screens.

  Closes #128
  ```

Diff: zmiana łamiąca API
- ✅
  ```
  feat(api)!: rename /v1/orders to /v1/checkout

  BREAKING CHANGE: clients on /v1/orders must migrate to /v1/checkout
  before 2026-06-01. Old route returns 410 after that date.
  ```

## Auto-jasność

Zawsze dodawaj treść dla: breaking changes, poprawek bezpieczeństwa, migracji danych i odwracania wcześniejszego commita. Nie ściskaj tego do samego tematu — przyszły debugger potrzebuje kontekstu.

## Granice

Ten skill tylko generuje wiadomość commita. Nie uruchamia `git commit`, nie stage’uje plików, nie robi amend. Zwracaj wiadomość jako blok kodu gotowy do wklejenia. „stop jaskiniowiec-commit” lub „normalny tryb”: wróć do dłuższego stylu.
