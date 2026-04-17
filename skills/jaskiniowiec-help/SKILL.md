---
name: jaskiniowiec-help
description: >
  Krótka karta referencyjna wszystkich trybów, skilli i komend jaskiniowca.
  Jednorazowy widok, nie trwały tryb. Wyzwalacze: /jaskiniowiec-help,
  „pomoc jaskiniowiec”, „jakie komendy ma jaskiniowiec”,
  „jak używać jaskiniowca”.
---

# Pomoc jaskiniowca

Pokaż tę kartę po wywołaniu. Jednorazowo — NIE zmieniaj trybu, nie zapisuj flag i niczego nie utrwalaj. Odpowiedź też ma być w stylu jaskiniowca.

## Tryby

| Tryb | Wyzwalacz | Co zmienia |
|------|-----------|-------------|
| **Lite** | `/jaskiniowiec lite` | Usuwa watę. Zostawia pełne zdania. |
| **Full** | `/jaskiniowiec` | Usuwa watę, grzeczności i asekurację. Urwane zdania OK. Domyślny. |
| **Ultra** | `/jaskiniowiec ultra` | Maksymalna kompresja. Nagie skróty. Tabele lepsze niż akapity. |

Tryb trwa do zmiany albo końca sesji.

## Skille

| Skill | Wyzwalacz | Co robi |
|-------|-----------|----------|
| **jaskiniowiec-commit** | `/jaskiniowiec-commit` | Zwięzłe wiadomości commitów. Conventional Commits. Temat ≤50 znaków. |
| **jaskiniowiec-review** | `/jaskiniowiec-review` | Jednolinijkowe komentarze do PR: `L42: bug: user null. Add guard.` |
| **jaskiniowiec-compress** | `/jaskiniowiec:compress <plik>` | Kompresuje pliki `.md` do stylu jaskiniowca. Oszczędza ~46% tokenów wejściowych. |
| **jaskiniowiec-help** | `/jaskiniowiec-help` | Ta karta. |

## Wyłączanie

Powiedz „stop jaskiniowiec” albo „normalny tryb”. Wrócisz w każdej chwili przez `/jaskiniowiec`.

## Konfiguracja domyślnego trybu

Domyślny tryb = `full`. Zmienisz go tak:

**Zmienna środowiskowa** (najwyższy priorytet):
```bash
export JASKINIOWIEC_DEFAULT_MODE=ultra
```

**Plik konfiguracyjny** (`~/.config/jaskiniowiec/config.json`):
```json
{ "defaultMode": "lite" }
```

Ustaw `"off"`, aby wyłączyć automatyczną aktywację na starcie sesji. Użytkownik nadal może włączyć tryb ręcznie przez `/jaskiniowiec`.

Rozstrzyganie: zmienna środowiskowa > plik konfiguracyjny > `full`.

## Więcej

Pełna dokumentacja forkowej wersji jest w tym repozytorium. Inspiracja upstreamem: https://github.com/JuliusBrussee/caveman
