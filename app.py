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


def code_tokens(value):
    """Return meaningful C# tokens with their source positions; whitespace is ignored."""
    pattern = re.compile(
        r'//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|'
        r'[A-Za-z_]\w*|\d+(?:\.\d+)?f?|'
        r'==|!=|<=|>=|=>|\+\+|--|\+=|-=|&&|\|\||\?\?|::|\?\.|[^\s]',
        re.S
    )
    return [(m.group(0), m.start(), m.end()) for m in pattern.finditer(value or "")]

def compare_code(user_code, expected_answers):
    """Align code tokens and mark matched tokens, returning best candidate comparison."""
    from difflib import SequenceMatcher

    user_code = user_code or ""
    user_tokens = code_tokens(user_code)
    user_values = [t[0] for t in user_tokens]
    best = None

    for expected in expected_answers:
        expected_tokens = code_tokens(expected)
        expected_values = [t[0] for t in expected_tokens]
        matcher = SequenceMatcher(a=expected_values, b=user_values, autojunk=False)
        matched_user = set()
        matched_expected = set()
        for block in matcher.get_matching_blocks():
            for offset in range(block.size):
                matched_expected.add(block.a + offset)
                matched_user.add(block.b + offset)

        total = len(expected_values)
        matched = len(matched_expected)
        percent = 100 if total == 0 else round(matched / total * 100)
        candidate = {
            "expected": expected,
            "matched_user": matched_user,
            "matched_expected": matched_expected,
            "user_tokens": user_tokens,
            "expected_tokens": expected_tokens,
            "percent": percent,
            "exact": normalize_code(user_code) == normalize_code(expected)
        }
        if best is None or (candidate["exact"], candidate["percent"]) > (best["exact"], best["percent"]):
            best = candidate

    return best

def show_code_comparison(user_code, comparison):
    """Render learner code with matched tokens green and incorrect/extra tokens red."""
    from html import escape

    tokens = comparison["user_tokens"]
    matched = comparison["matched_user"]
    parts = []
    cursor = 0
    for i, (token, start, end) in enumerate(tokens):
        parts.append(escape(user_code[cursor:start]))
        color = "#16803c" if i in matched else "#d92d20"
        bg = "#e8f7ed" if i in matched else "#fff0ee"
        parts.append(
            f'<span style="color:{color};background:{bg};font-weight:600;border-radius:3px;">'
            f'{escape(token)}</span>'
        )
        cursor = end
    parts.append(escape(user_code[cursor:]))
    html_code = "".join(parts) or "<span>(prazan odgovor)</span>"
    st.markdown(
        '<div style="border:1px solid #8885;border-radius:8px;padding:12px;'
        'overflow-x:auto;white-space:pre-wrap;font-family:monospace;line-height:1.55;">'
        + html_code + '</div>',
        unsafe_allow_html=True
    )

    missing = [
        token for i, (token, _, _) in enumerate(comparison["expected_tokens"])
        if i not in comparison["matched_expected"]
    ]
    if missing:
        st.markdown("**Dijelovi rješenja koji nedostaju:**")
        st.markdown(
            '<div style="color:#d92d20;background:#fff0ee;border-radius:6px;'
            'padding:8px;font-family:monospace;white-space:pre-wrap;">'
            + escape(" ".join(missing)) + '</div>',
            unsafe_allow_html=True
        )
    else:
        st.success("Svi potrebni dijelovi rješenja su prepoznati.")


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
        partial_w = sum(v.get("partial", False) for v in answers_w.values())
        bad_w = sum(v["ok"] is False and not v.get("partial", False) for v in answers_w.values())
        st.write(f"Odgovoreno: **{done_w}/{Nw}**  ·  Točno: **{good_w}**  ·  Djelomično: **{partial_w}**  ·  Netočno: **{bad_w}**")
        st.progress(done_w / Nw if Nw else 0)
        if st.button("🔀 Novi nasumični pisani pokušaj", key="reset_written"):
            reset_quiz("written", Nw)
            st.rerun()

    if pos_w >= Nw:
        good_w = sum(v["ok"] is True for v in answers_w.values())
        partial_w = sum(v.get("partial", False) for v in answers_w.values())
        bad_w = sum(v["ok"] is False and not v.get("partial", False) for v in answers_w.values())
        st.success("🏁 Pisani kviz je završen!")
        st.metric("Potpuno točni odgovori", f"{good_w}/{Nw}", f"{round(good_w/Nw*100)}%")
        st.write(f"Točno: {good_w} · Djelomično točno: {partial_w} · Netočno: {bad_w}")
        with st.expander("Pitanja za ponavljanje"):
            for qi, result in answers_w.items():
                if result["ok"] is not True:
                    q = written[qi]
                    st.markdown(f"**{q['id']}. {q['question']}**")
                    accepted = q.get("accepted_answers", [q["answer"]])
                    comparison = compare_code(result["choice"], accepted)
                    st.write("Tvoj odgovor: zeleno = prepoznat dio, crveno = pogrešan ili dodatni dio")
                    show_code_comparison(result["choice"], comparison)
                    st.write("Točan odgovor prema skripti:")
                    st.code(comparison["expected"], language="csharp")
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
                accepted = q_w.get("accepted_answers", [q_w["answer"]])
                comparison = compare_code(typed, accepted)
                answers_w[idx_w] = {
                    "ok": comparison["exact"],
                    "partial": (not comparison["exact"] and comparison["percent"] > 0),
                    "percent": comparison["percent"],
                    "choice": typed
                }
                st.rerun()
        else:
            accepted = q_w.get("accepted_answers", [q_w["answer"]])
            comparison = compare_code(prev_w["choice"], accepted)
            if prev_w["ok"]:
                st.success("Točno! Svi bitni dijelovi koda odgovaraju rješenju. 🎉")
            elif prev_w.get("partial"):
                st.warning(f"Djelomično točno: prepoznato je približno {prev_w['percent']}% bitnih dijelova.")
            else:
                st.error("Još nije prepoznat nijedan odgovarajući dio rješenja.")
            st.write("Tvoj odgovor: zeleno = prepoznat dio, crveno = pogrešan ili dodatni dio")
            show_code_comparison(prev_w["choice"], comparison)
            st.write("Točan odgovor prema skripti:")
            st.code(comparison["expected"], language="csharp")
            st.caption("Usporedba gleda redoslijed C# riječi, naziva, brojeva i operatora. Razmaci i prijelomi redaka se zanemaruju.")

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
