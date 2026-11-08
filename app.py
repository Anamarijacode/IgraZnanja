import streamlit as st, json, re, unicodedata, random
from pathlib import Path
st.set_page_config(page_title="Unity i C# ABCD kviz", page_icon="🎮", layout="centered")
@st.cache_data
def load():
    return json.loads(Path(__file__).with_name("questions.json").read_text(encoding="utf-8"))
qs=load(); N=len(qs)
def fresh():
    st.session_state.order=list(range(N)); random.shuffle(st.session_state.order)
    st.session_state.pos=0; st.session_state.answers={}
if "order" not in st.session_state: fresh()
st.title("🎮 Unity i C# | ABCD kviz")
st.caption("170 pitanja iz tvoje skripte • automatska provjera • rezultat i ponavljanje")
with st.sidebar:
    done=len(st.session_state.answers)
    good=sum(v["ok"] is True for v in st.session_state.answers.values())
    bad=sum(v["ok"] is False for v in st.session_state.answers.values())
    st.header("Tvoj rezultat")
    st.metric("Odgovoreno",f"{done}/{N}")
    st.metric("Točno",good); st.metric("Netočno",bad)
    st.progress(done/N)
    if st.button("🔀 Novi nasumični pokušaj",use_container_width=True):
        fresh(); st.rerun()
    if st.button("♻️ Resetiraj redom",use_container_width=True):
        st.session_state.order=list(range(N)); st.session_state.pos=0; st.session_state.answers={}; st.rerun()
if st.session_state.pos>=N:
    good=sum(v["ok"] is True for v in st.session_state.answers.values())
    bad=sum(v["ok"] is False for v in st.session_state.answers.values())
    skipped=sum(v["ok"] is None for v in st.session_state.answers.values())
    st.balloons(); st.header("🏁 Kviz završen!")
    st.metric("Rezultat",f"{good}/{N}",f"{round(good/N*100)}%")
    st.write(f"Točno: {good} · Netočno: {bad} · Preskočeno: {skipped}")
    st.subheader("Pitanja za ponavljanje")
    for qi,r in st.session_state.answers.items():
        if r["ok"] is not True:
            q=qs[qi]
            with st.expander(f"{q['id']}. {q['question']}"):
                st.write("Tvoj odgovor:",r["choice"])
                st.write("Odgovor iz skripte:",q["answer"])
    if st.button("Ponovi kviz",type="primary"): fresh(); st.rerun()
    st.stop()
idx=st.session_state.order[st.session_state.pos]; q=qs[idx]
st.progress(st.session_state.pos/N)
st.caption(f"Pitanje {st.session_state.pos+1} od {N} • Izvorno pitanje #{q['id']}")
st.markdown("### "+q["question"])
prev=st.session_state.answers.get(idx)
if q["unavailable"]:
    st.warning("Odgovor u izvornoj skripti nije čitljiv. Ovo pitanje možeš preskočiti.")
    if prev is None and st.button("Preskoči pitanje",type="primary"):
        st.session_state.answers[idx]={"ok":None,"choice":"Preskočeno"}; st.rerun()
elif prev is None:
    letters=["A","B","C","D"]
    choice=st.radio("Odaberi jedan odgovor:",range(4),format_func=lambda i:f"{letters[i]}) {q['options'][i]}",index=None,key=f"choice_{idx}")
    if st.button("Provjeri odgovor",type="primary",use_container_width=True,disabled=choice is None):
        st.session_state.answers[idx]={"ok":choice==q["correct_index"],"choice":f"{letters[choice]}) {q['options'][choice]}"}
        st.rerun()
else:
    if prev["ok"]: st.success("Točno! 🎉")
    else: st.error("Nije točno. Ovo pitanje ide na ponavljanje.")
    st.write("Tvoj odgovor:",prev["choice"])
    st.info("Točan odgovor prema skripti: "+q["answer"])
st.divider()
c1,c2=st.columns(2)
with c1:
    if st.button("⬅ Prethodno",disabled=st.session_state.pos==0,use_container_width=True):
        st.session_state.pos-=1; st.rerun()
with c2:
    if st.button("Sljedeće ➜",type="primary",use_container_width=True):
        if idx not in st.session_state.answers: st.warning("Prvo odaberi odgovor ili preskoči pitanje.")
        else: st.session_state.pos+=1; st.rerun()
st.caption("Pitanja i točni odgovori preuzeti su iz tvoje skripte. ABCD distraktori su odabrani iz ostalih odgovora u istoj skripti.")
