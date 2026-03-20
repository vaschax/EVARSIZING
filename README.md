# EVAR sizing prototype

Prototyp aplikacji `Streamlit` do wspomagania planowania EVAR na podstawie wymiarów aorty i tętnic biodrowych.

## Co zawiera

- `app.py`: interfejs użytkownika.
- `evar_data.py`: jawne tabele rozmiarów przepisane z załączonych PDF-ów.
- `recommender.py`: logika dopasowania i ostrzeżeń.

## Uruchomienie w VS Code

1. Otwórz folder projektu w VS Code.
2. W terminalu VS Code aktywuj lokalne środowisko:

```bash
source .venv/bin/activate
```

3. Uruchom aplikację:

```bash
streamlit run app.py
```

## Ważne

- To jest prototyp wspomagający planowanie, a nie samodzielne narzędzie do decyzji klinicznej.
- Logika Cook i Gore jest oparta o jawne tabele z załączonych worksheetów.
- Logika Medtronic jest częściowo heurystyczna, ponieważ załączony PDF podaje rozmiary urządzenia, ale nie pełne zakresy naczyń.
