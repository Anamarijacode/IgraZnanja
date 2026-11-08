# Unity i C# ABCD kviz (170 pitanja)

## Pokretanje lokalno
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Besplatno online preko Streamlit Community Cloud
1. Napravi GitHub račun i novi repository.
2. Učitaj `app.py`, `questions.json` i `requirements.txt`.
3. Otvori https://share.streamlit.io/ i prijavi se GitHubom.
4. Klikni Create app, odaberi repository, branch `main` i datoteku `app.py`.
5. Klikni Deploy.

Aplikacija prikazuje jedno ABCD pitanje, automatski provjerava odabir, prati rezultat i prikazuje pitanja za ponavljanje. Pitanja i točni odgovori su iz korisničke skripte. Ponuđeni netočni odgovori su sastavljeni od drugih odgovora iz iste skripte. Jedan izvorni odgovor nije čitljiv pa se to pitanje može preskočiti.
