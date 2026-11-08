import streamlit as st, json, random
from pathlib import Path
st.set_page_config(page_title="Unity i C# | ABCD kviz",page_icon="🎮",layout="centered")
@st.cache_data
def load(): return json.loads(Path(__file__).with_name("questions.json").read_text(encoding="utf-8"))
Q=load(); N=len(Q)
def reset(shuffle=True):
    st.session_state.order=list(range(N))
    if shuffle: random.shuffle(st.session_state.order)
    st.session_state.pos=0; st.session_state.results={}
if "order" not in st.session_state: reset(True)
with st.sidebar:
    done=len(st.session_state.results)
    correct=sum(x["ok"] is True for x in st.session_state.results.values())
    wrong=sum(x["ok"] is False for x in st.session_state.results.values())
    st.header("📊 Tvoj rezultat")
    st.metric("Odgovoreno",f"{done}/{N}"); st.metric("Točno",correct); st.metric("Netočno",wrong)
    st.progress(done/N)
    if st.button("🔀 Novi nasumični kviz",use_container_width=True): reset(True); st.rerun()
    if st.button("📚 Pitanja redom",use_container_width=True): reset(False); st.rerun()
st.title("🎮 Unity i C#")
st.caption("170 pitanja • ABCD • automatska provjera • pregled pogrešaka")
if st.session_state.pos>=N:
    correct=sum(x["ok"] is True for x in st.session_state.results.values())
    wrong=sum(x["ok"] is False for x in st.session_state.results.values())
    skipped=sum(x["ok"] is None for x in st.session_state.results.values())
    st.balloons(); st.header("🏁 Kviz završen!")
    st.metric("Konačni rezultat",f"{correct}/{N}",f"{round(correct/N*100)}%")
    st.write(f"Točno: **{correct}** · Netočno: **{wrong}** · Preskočeno: **{skipped}**")
    st.subheader("Pitanja za ponavljanje")
    for idx,r in st.session_state.results.items():
        if r["ok"] is not True:
            q=Q[idx]
            with st.expander(f"{q['id']}. {q['question']}"):
                st.write("Tvoj odgovor:",r["selected"]); st.write("Točan odgovor:",q["answer"])
    if st.button("Ponovi kviz",type="primary"): reset(True); st.rerun()
    st.stop()
idx=st.session_state.order[st.session_state.pos]; q=Q[idx]
st.progress(st.session_state.pos/N)
st.caption(f"Pitanje {st.session_state.pos+1} od {N} • Izvorno pitanje #{q['id']}")
st.markdown("### "+q["question"])
old=st.session_state.results.get(idx)
if q["unavailable"]:
    st.warning("Odgovor u izvornoj skripti nije čitljiv. Ovo pitanje možeš preskočiti.")
    if old is None and st.button("Preskoči pitanje",type="primary"):
        st.session_state.results[idx]={"ok":None,"selected":"Preskočeno"}; st.rerun()
elif old is None:
    letters=["A","B","C","D"]
    choice=st.radio("Odaberi jedan odgovor:",range(4),format_func=lambda j:f"{letters[j]}) {q['options'][j]}",index=None,key=f"choice_{idx}")
    if st.button("Provjeri odgovor",type="primary",use_container_width=True,disabled=choice is None):
        st.session_state.results[idx]={"ok":choice==q["correct_index"],"selected":f"{letters[choice]}) {q['options'][choice]}"}
        st.rerun()
else:
    if old["ok"]: st.success("Točno! 🎉")
    else: st.error("Netočno. Pogledaj točan odgovor.")
    st.write("Tvoj odgovor:",old["selected"])
    st.info("Točan odgovor prema tvojoj skripti: **"+q["answer"]+"**")
st.divider()
a,b=st.columns(2)
with a:
    if st.button("⬅ Prethodno",disabled=st.session_state.pos==0,use_container_width=True):
        st.session_state.pos-=1; st.rerun()
with b:
    if st.button("Sljedeće ➜",type="primary",use_container_width=True):
        if idx not in st.session_state.results: st.warning("Prvo odaberi odgovor ili preskoči pitanje.")
        else: st.session_state.pos+=1; st.rerun()
st.caption("ABCD opcije su ručno prilagođene vrsti pitanja. Točan odgovor ostaje iz tvoje izvorne skripte.")
