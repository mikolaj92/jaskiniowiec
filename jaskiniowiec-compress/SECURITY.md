# Bezpieczeństwo

## Ocena Snyk High Risk

`jaskiniowiec-compress` dostaje w Snyk ocenę High Risk z powodu heurystyk analizy statycznej. Ten dokument wyjaśnia, co skill robi, a czego nie robi.

### Co wyzwala ocenę

1. **Użycie `subprocess`**: skill wywołuje CLI `claude` przez `subprocess.run()` jako fallback, gdy nie ma ustawionego `ANTHROPIC_API_KEY`. Wywołanie używa stałej listy argumentów — nie ma interpolacji shellowej. Treść pliku użytkownika trafia przez stdin, nie jako argument shella.

2. **Odczyt i zapis plików**: skill czyta plik wskazany jawnie przez użytkownika, kompresuje go i zapisuje wynik z powrotem pod tą samą ścieżką. Obok zapisuje backup `.original.md`. Nie czyta ani nie zapisuje plików poza ścieżką wskazaną przez użytkownika.

### Czego skill NIE robi

- Nie uruchamia treści pliku użytkownika jako kodu
- Nie wykonuje żądań sieciowych poza API Anthropic (przez SDK albo CLI)
- Nie sięga do plików poza ścieżką podaną przez użytkownika
- Nie używa `shell=True` ani interpolacji stringów w wywołaniach `subprocess`
- Nie zbiera ani nie przesyła danych innych niż kompresowany plik

### Zachowanie uwierzytelniania

Jeśli ustawiono `ANTHROPIC_API_KEY`, skill używa bezpośrednio Anthropic Python SDK, bez `subprocess`. Jeśli nie, przechodzi na CLI `claude`, które korzysta z istniejącego uwierzytelnienia użytkownika w Claude.

### Limit rozmiaru pliku

Pliki większe niż 500 KB są odrzucane przed jakimkolwiek wywołaniem API.

### Zgłoszenie podatności

Jeśli uważasz, że znalazłeś prawdziwy problem bezpieczeństwa, otwórz issue na GitHubie z etykietą `security`.
