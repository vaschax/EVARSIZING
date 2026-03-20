# EVAR sizing prototype

Prototyp aplikacji `Streamlit` do wspomagania planowania EVAR na podstawie wymiarów aorty i tętnic biodrowych.

## Disclaimer kliniczny

Narzędzie wyłącznie do celów edukacyjnych i poglądowych. Ostateczny dobór sprzętu musi odbywać się w oparciu o stację roboczą
(np. 3mensio, OsiriX, TeraRecon) i oficjalne instrukcje użytkowania (IFU) producenta. Autor oprogramowania nie ponosi
odpowiedzialności klinicznej za decyzje podjęte na podstawie tego prototypu.

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
- W aplikacji jest liczony oversizing oraz pokazywane są ostrzeżenia hostile anatomy i overlap, ale nadal należy je traktować jako wsparcie planowania, a nie ostateczne IFU.
