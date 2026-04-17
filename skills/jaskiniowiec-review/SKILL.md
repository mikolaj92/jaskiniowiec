---
name: jaskiniowiec-review
description: >
  Ultra-zwięzłe komentarze do code review. Wycina szum z feedbacku do PR,
  ale zostawia konkret. Każdy komentarz to jedna linia: lokalizacja,
  problem, poprawka. Użyj, gdy użytkownik mówi „zrób review PR-a”,
  „code review”, „przejrzyj diff” albo wywołuje /jaskiniowiec-review.
  Włącza się też podczas przeglądu pull requestów.
---

Pisz komentarze code review krótko i konkretnie. Jedna linia na znalezisko. Lokalizacja, problem, poprawka. Bez przydługich wstępów.

## Zasady

**Format:** `L<linia>: <problem>. <poprawka>.` — albo `<plik>:L<linia>: ...` przy diffach wieloplikowych.

**Prefiks ważności (opcjonalny):**
- `🔴 bug:` — zepsute zachowanie, realny incydent
- `🟡 risk:` — działa, ale kruche (race, brak null checka, połknięty błąd)
- `🔵 nit:` — styl, nazewnictwo, mikrooptymalizacja; autor może zignorować
- `❓ q:` — prawdziwe pytanie, nie sugestia

**Usuń:**
- „I noticed that...”, „It seems like...”, „You might want to consider..."
- „This is just a suggestion but...” — użyj `nit:`
- „Great work!”, „Looks good overall but...” — najwyżej raz na początku, nie przy każdym komentarzu
- Przepisywanie tego, co linia już robi — reviewer widzi diff
- Asekurację („perhaps”, „maybe”, „I think”) — jeśli nie masz pewności, użyj `q:`

**Zostaw:**
- Dokładne numery linii
- Dokładne nazwy symboli/funkcji/zmiennych w backtickach
- Konkretną poprawkę, nie ogólne „można by zrefaktoryzować”
- *Dlaczego*, jeśli nie wynika wprost z opisu problemu

## Przykłady

❌ "I noticed that on line 42 you're not checking if the user object is null before accessing the email property. This could potentially cause a crash if the user is not found in the database. You might want to add a null check here."

✅ `L42: 🔴 bug: user can be null after .find(). Add guard before .email.`

❌ "It looks like this function is doing a lot of things and might benefit from being broken up into smaller functions for readability."

✅ `L88-140: 🔵 nit: 50-line fn does 4 things. Extract validate/normalize/persist.`

❌ "Have you considered what happens if the API returns a 429? I think we should probably handle that case."

✅ `L23: 🟡 risk: no retry on 429. Wrap in withBackoff(3).`

## Auto-jasność

Wyłącz tryb zwięzły dla: ustaleń bezpieczeństwa klasy CVE, sporów architektonicznych wymagających uzasadnienia oraz sytuacji onboardingowych, gdy autor potrzebuje szerszego „dlaczego”. Wtedy napisz normalny akapit, potem wróć do zwięzłego stylu.

## Granice

Tylko review — bez pisania poprawki w kodzie, bez approve/request-changes, bez uruchamiania linterów. Zwracaj komentarze gotowe do wklejenia do PR-a. „stop jaskiniowiec-review” lub „normalny tryb”: wróć do dłuższego review.
