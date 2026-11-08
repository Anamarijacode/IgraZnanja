import streamlit as st
import json, random, re
from pathlib import Path

st.set_page_config(page_title="Unity i C# kviz", page_icon="🎮", layout="centered")

@st.cache_data
def load_data():
    folder = Path(__file__).parent
    abcd = json.loads((folder / "questions_abcd.json").read_text(encoding="utf-8"))
    written = json.loads((folder / "questions_written.json").read_text(encoding="utf-8"))
    return abcd, written

abcd, written = load_data()

def normalize_code(value):
    value = value or ""
    value = value.replace("```csharp", "").replace("```cs", "").replace("```", "")
    value = value.replace("`", "")
    value = value.replace("\u00a0", " ")
    # Ignore whitespace only. C# identifiers, punctuation and capitalization remain significant.
    return re.sub(r"\s+", "", value)

def init_quiz(prefix, total):
    order_key = f"{prefix}_order"
    pos_key = f"{prefix}_pos"
    answers_key = f"{prefix}_answers"
    if order_key not in st.session_state:
        order = list(range(total))
        random.shuffle(order)
        st.session_state[order_key] = order
        st.session_state[pos_key] = 0
        st.session_state[answers_key] = {}

def reset_quiz(prefix, total, shuffle=True):
    order = list(range(total))
    if shuffle:
        random.shuffle(order)
    st.session_state[f"{prefix}_order"] = order
    st.session_state[f"{prefix}_pos"] = 0
    st.session_state[f"{prefix}_answers"] = {}

st.title("🎮 Unity i C# kviz")
st.caption("Ukupno 262 pitanja iz tvojih materijala: 170 ABCD + 92 pisana.")

tab_abcd, tab_written = st.tabs(["🅰️ ABCD pitanja (170)", "⌨️ Pisana pitanja (92)"])

with tab_abcd:
    N = len(abcd)
    init_quiz("abcd", N)
    order = st.session_state.abcd_order
    pos = st.session_state.abcd_pos
    answers = st.session_state.abcd_answers

    with st.expander("📊 Rezultat ABCD kviza", expanded=False):
        done = len(answers)
        good = sum(v["ok"] is True for v in answers.values())
        bad = sum(v["ok"] is False for v in answers.values())
        st.write(f"Odgovoreno: **{done}/{N}**  ·  Točno: **{good}**  ·  Netočno: **{bad}**")
        st.progress(done / N if N else 0)
        if st.button("🔀 Novi nasumični ABCD pokušaj", key="reset_abcd"):
            reset_quiz("abcd", N)
            st.rerun()

    if pos >= N:
        good = sum(v["ok"] is True for v in answers.values())
        bad = sum(v["ok"] is False for v in answers.values())
        skipped = sum(v["ok"] is None for v in answers.values())
        st.success("🏁 ABCD kviz je završen!")
        st.metric("Rezultat", f"{good}/{N}", f"{round(good/N*100)}%")
        st.write(f"Točno: {good} · Netočno: {bad} · Preskočeno: {skipped}")
        with st.expander("Pitanja za ponavljanje"):
            for qi, result in answers.items():
                if result["ok"] is not True:
                    q = abcd[qi]
                    st.markdown(f"**{q['id']}. {q['question']}**")
                    st.write("Tvoj odgovor:", result["choice"])
                    st.write("Odgovor iz skripte:", q["answer"])
        if st.button("Ponovi ABCD kviz", key="repeat_abcd", type="primary"):
            reset_quiz("abcd", N)
            st.rerun()
    else:
        idx = order[pos]
        q = abcd[idx]
        st.progress(pos / N)
        st.caption(f"Pitanje {pos+1} od {N} · Izvorno pitanje #{q['id']}")
        st.markdown("### " + q["question"])
        previous = answers.get(str(idx), answers.get(idx))

        if q.get("unavailable"):
            st.warning("Odgovor u izvornoj skripti nije čitljiv. Ovo pitanje možeš preskočiti.")
            if previous is None and st.button("Preskoči pitanje", key=f"skip_{idx}"):
                answers[idx] = {"ok": None, "choice": "Preskočeno"}
                st.rerun()
        elif previous is None:
            letters = ["A", "B", "C", "D"]
            choice = st.radio(
                "Odaberi jedan odgovor:",
                range(4),
                format_func=lambda i: f"{letters[i]}) {q['options'][i]}",
                index=None,
                key=f"abcd_choice_{idx}"
            )
            if st.button("Provjeri odgovor", type="primary", key=f"check_abcd_{idx}", disabled=choice is None):
                answers[idx] = {
                    "ok": choice == q["correct_index"],
                    "choice": f"{letters[choice]}) {q['options'][choice]}"
                }
                st.rerun()
        else:
            if previous["ok"] is True:
                st.success("Točno! 🎉")
            elif previous["ok"] is False:
                st.error("Nije točno. Ovo pitanje ide na ponavljanje.")
            else:
                st.info("Pitanje je preskočeno.")
            st.write("Tvoj odgovor:", previous["choice"])
            st.info("Točan odgovor prema skripti: " + q["answer"])

        c1, c2 = st.columns(2)
        with c1:
            if st.button("⬅ Prethodno", key=f"prev_abcd_{pos}", disabled=pos == 0, use_container_width=True):
                st.session_state.abcd_pos -= 1
                st.rerun()
        with c2:
            if st.button("Sljedeće ➜", key=f"next_abcd_{pos}", type="primary", use_container_width=True):
                if idx not in answers:
                    st.warning("Prvo odaberi odgovor ili preskoči pitanje.")
                else:
                    st.session_state.abcd_pos += 1
                    st.rerun()

with tab_written:
    Nw = len(written)
    init_quiz("written", Nw)
    order_w = st.session_state.written_order
    pos_w = st.session_state.written_pos
    answers_w = st.session_state.written_answers

    with st.expander("📊 Rezultat pisanog kviza", expanded=False):
        done_w = len(answers_w)
        good_w = sum(v["ok"] is True for v in answers_w.values())
        bad_w = sum(v["ok"] is False for v in answers_w.values())
        st.write(f"Odgovoreno: **{done_w}/{Nw}**  ·  Točno: **{good_w}**  ·  Netočno: **{bad_w}**")
        st.progress(done_w / Nw if Nw else 0)
        if st.button("🔀 Novi nasumični pisani pokušaj", key="reset_written"):
            reset_quiz("written", Nw)
            st.rerun()

    if pos_w >= Nw:
        good_w = sum(v["ok"] is True for v in answers_w.values())
        bad_w = sum(v["ok"] is False for v in answers_w.values())
        st.success("🏁 Pisani kviz je završen!")
        st.metric("Točni odgovori", f"{good_w}/{Nw}", f"{round(good_w/Nw*100)}%")
        st.write(f"Točno: {good_w} · Netočno: {bad_w}")
        with st.expander("Pitanja za ponavljanje"):
            for qi, result in answers_w.items():
                if result["ok"] is not True:
                    q = written[qi]
                    st.markdown(f"**{q['id']}. {q['question']}**")
                    st.code(result["choice"] or "(prazan odgovor)", language="csharp")
                    st.write("Točan odgovor prema skripti:")
                    st.code(q["answer"], language="csharp")
        if st.button("Ponovi pisani kviz", key="repeat_written", type="primary"):
            reset_quiz("written", Nw)
            st.rerun()
    else:
        idx_w = order_w[pos_w]
        q_w = written[idx_w]
        st.progress(pos_w / Nw)
        st.caption(f"Pitanje {pos_w+1} od {Nw} · Izvorno pitanje #{q_w['id']}")
        st.markdown("### " + q_w["question"])
        prev_w = answers_w.get(str(idx_w), answers_w.get(idx_w))

        if prev_w is None:
            typed = st.text_area(
                "Upiši C# kod ili funkciju:",
                height=180,
                key=f"written_input_{idx_w}",
                placeholder="Ovdje napiši svoj odgovor..."
            )
            if st.button("Provjeri odgovor", type="primary", key=f"check_written_{idx_w}", disabled=not typed.strip()):
                accepted = q_w.get("accepted_answers", [q_w["answer"]])\n                ok = any(normalize_code(typed) == normalize_code(expected) for expected in accepted)
                answers_w[idx_w] = {"ok": ok, "choice": typed}
                st.rerun()
        else:
            if prev_w["ok"]:
                st.success("Točno! 🎉")
            else:
                st.error("Odgovor se ne podudara s rješenjem iz skripte.")
            st.write("Tvoj odgovor:")
            st.code(prev_w["choice"], language="csharp")
            st.write("Točan odgovor prema skripti:")
            st.code(q_w["answer"], language="csharp")
            st.caption("Provjera zanemaruje razmake i prijelome redaka, ali provjerava nazive, znakove i velika/mala slova.")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("⬅ Prethodno", key=f"prev_written_{pos_w}", disabled=pos_w == 0, use_container_width=True):
                st.session_state.written_pos -= 1
                st.rerun()
        with c2:
            if st.button("Sljedeće ➜", key=f"next_written_{pos_w}", type="primary", use_container_width=True):
                if idx_w not in answers_w:
                    st.warning("Prvo napiši i provjeri odgovor.")
                else:
                    st.session_state.written_pos += 1
                    st.rerun()

st.divider()
st.caption("Pitanja i rješenja preuzeti su iz dostavljenih materijala. Pisani odgovori provjeravaju se automatski prema zapisanom rješenju.")
