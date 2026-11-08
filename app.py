import streamlit as st
import json
import re
import unicodedata
from pathlib import Path

st.set_page_config(page_title="Unity i C# | Kviz", page_icon="🎮", layout="centered")

@st.cache_data
def load_questions():
    data = json.loads(Path(__file__).with_name("questions.json").read_text(encoding="utf-8"))
    return data

def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "").casefold().strip()
    value = value.replace("`", "").replace("’", "'").replace("“", '"').replace("”", '"')
    value = re.sub(r"\s+", " ", value)
    # Ignore harmless whitespace differences around code punctuation.
    value = re.sub(r"\s*([(),;<>])\s*", r"\1", value)
    return value.strip().rstrip(" .;")

def is_correct(user_answer: str, expected: str) -> bool:
    user = normalize(user_answer)
    expected = normalize(expected)
    if not user:
        return False

    # The source sometimes lists equivalent alternatives separated by slash.
    alternatives = [part.strip() for part in re.split(r"\s*/\s*", expected) if part.strip()]
    return any(user == part for part in alternatives) or user == expected

def init_state():
    defaults = {
        "index": 0,
        "results": {},
        "checked": False,
        "last_user_answer": "",
        "mode": "all",
        "order": list(range(len(load_questions()))),
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

questions = load_questions()
init_state()
total = len(questions)

st.title("🎮 Unity i C#")
st.caption(f"Interaktivni kviz iz tvoje skripte • svih {total} pitanja")

with st.sidebar:
    st.header("Tvoj napredak")
    answered = len(st.session_state.results)
    correct = sum(1 for x in st.session_state.results.values() if x["correct"] is True)
    wrong = sum(1 for x in st.session_state.results.values() if x["correct"] is False)
    st.metric("Odgovoreno", f"{answered}/{total}")
    st.metric("Točno", correct)
    st.metric("Za ponavljanje", wrong)
    st.progress(answered / total if total else 0)
    st.divider()
    if st.button("🔄 Kreni ispočetka", use_container_width=True):
        for key in ["index", "results", "checked", "last_user_answer", "mode", "order"]:
            st.session_state.pop(key, None)
        st.rerun()

def show_finish():
    st.success("Bravo! Došla si do kraja kviza.")
    answered = len(st.session_state.results)
    correct = sum(1 for x in st.session_state.results.values() if x["correct"] is True)
    wrong = sum(1 for x in st.session_state.results.values() if x["correct"] is False)
    skipped = sum(1 for x in st.session_state.results.values() if x["correct"] is None)
    st.subheader(f"Rezultat: {correct} / {answered}")
    if answered:
        st.write(f"Točno: **{correct}** · Netočno: **{wrong}** · Preskočeno/nečitljivo: **{skipped}**")
        st.write(f"Uspješnost među provjerenim odgovorima: **{round(correct / max(correct + wrong, 1) * 100)}%**")
    else:
        st.info("Još nema odgovorenih pitanja.")
    missed = [i for i, r in st.session_state.results.items() if r["correct"] is False]
    if missed:
        st.subheader("Pitanja za ponavljanje")
        for i in missed:
            st.markdown(f"**{i+1}. {questions[i]['question']}**")
            st.write(f"Točan odgovor: `{questions[i]['answer']}`")
    if st.button("Ponovi cijeli kviz", type="primary"):
        st.session_state.index = 0
        st.session_state.results = {}
        st.session_state.checked = False
        st.session_state.last_user_answer = ""
        st.rerun()

idx = st.session_state.index
if idx >= total:
    show_finish()
    st.stop()

q = questions[idx]
expected = q["answer"]
unavailable = "[suspicious link removed]" in expected

st.progress(idx / total)
st.caption(f"Pitanje {idx + 1} od {total}")

st.markdown(f"### {q['question']}")

if unavailable:
    st.warning("Odgovor za ovo pitanje nije čitljiv u izvornoj skripti. Neću izmišljati točan odgovor. Možeš ga preskočiti.")

if idx in st.session_state.results:
    result = st.session_state.results[idx]
    if result["correct"] is True:
        st.success("Točno! Odlično. ✅")
    elif result["correct"] is False:
        st.error("Nije točno. Nema veze, ovo ide na ponavljanje.")
        st.info(f"Točan odgovor prema tvojoj skripti: **{expected}**")
    else:
        st.warning("Pitanje je preskočeno jer odgovor u izvornoj skripti nije čitljiv.")
    if st.button("Sljedeće pitanje ➜", type="primary", use_container_width=True):
        st.session_state.index += 1
        st.rerun()
else:
    with st.form(key=f"answer_form_{idx}"):
        user_answer = st.text_input(
            "Tvoj odgovor",
            placeholder="Upiši odgovor ovdje…",
            key=f"answer_{idx}",
            disabled=unavailable,
        )
        submitted = st.form_submit_button("Provjeri odgovor", type="primary", use_container_width=True)
    if submitted:
        if unavailable:
            st.session_state.results[idx] = {"correct": None, "answer": ""}
        elif not user_answer.strip():
            st.warning("Upiši odgovor prije provjere.")
            st.stop()
        else:
            ok = is_correct(user_answer, expected)
            st.session_state.results[idx] = {"correct": ok, "answer": user_answer}
        st.rerun()

st.divider()
col1, col2 = st.columns(2)
with col1:
    if st.button("⬅ Prethodno", disabled=(idx == 0), use_container_width=True):
        st.session_state.index -= 1
        st.rerun()
with col2:
    if idx in st.session_state.results:
        if st.button("Nastavi ➜", use_container_width=True):
            st.session_state.index += 1
            st.rerun()

st.caption("Odgovori se provjeravaju prema odgovorima iz tvoje izvorne skripte. Velika/mala slova i višak razmaka ne utječu na provjeru. Kod odgovora je važno napisati ispravan izraz.")
