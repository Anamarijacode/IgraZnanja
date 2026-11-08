# Unity i C# kviz (170 pitanja)

## Pokretanje na računalu

1. Instaliraj Python 3.10 ili noviji.
2. Otvori terminal u ovoj mapi.
3. Pokreni:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Aplikacija će se otvoriti u pregledniku na lokalnoj adresi koju Streamlit ispiše.

## Besplatno objavljivanje online

Najjednostavnija opcija je Streamlit Community Cloud:

1. Napravi besplatan račun na GitHubu.
2. Napravi novi javni repository i u njega učitaj `app.py`, `questions.json` i `requirements.txt`.
3. Otvori https://share.streamlit.io/ i prijavi se GitHubom.
4. Klikni **Create app**, odaberi repository, branch `main` i datoteku `app.py`.
5. Klikni **Deploy**.

Dobit ćeš javni link koji možeš otvoriti na računalu ili mobitelu.

## Napomena o izvoru

Kviz sadrži svih 170 parova pitanja i odgovora iz dostavljene skripte. Jedan odgovor u izvornoj skripti prikazan je kao `[suspicious link removed]`; aplikacija ga zato označava kao nečitljiv i nudi preskakanje umjesto da izmisli odgovor.
