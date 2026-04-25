"""Streamlit UI - Country Information AI Agent."""

import streamlit as st
from src import run_agent

st.set_page_config(
    page_title="Country Information AI Agent",
    page_icon="🌍",
    layout="wide"
)

st.title("Country Information AI Agent")
st.write("Ask me anything about countries!")

st.divider()

examples = [
    ("Population of Germany?", "What is the population of Germany?"),
    ("Currency of Japan?", "What currency does Japan use?"),
    ("Capital of Brazil?", "What is the capital of Brazil?"),
    ("Languages of France?", "What languages are spoken in France?"),
    ("About Canada?", "Tell me about Canada"),
]

for label, query in examples:
    if st.button(label):
        st.session_state.pending_query = query

st.divider()

if "history" not in st.session_state:
    st.session_state.history = []

for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

query = st.chat_input("Ask about a country...")

if query:
    st.session_state.pending_query = query

if "pending_query" in st.session_state:
    q = st.session_state.pop("pending_query")
    st.session_state.history.append({"role": "user", "content": q})
    
    with st.spinner("🤔 Thinking..."):
        try:
            result = run_agent(q)
        except Exception as e:
            result = f"Error: {e}"
    
    st.session_state.history.append({"role": "assistant", "content": result})
    st.rerun()