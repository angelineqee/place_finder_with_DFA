# app.py  (Streamlit front-end, prettier layout)
import pandas as pd
import streamlit as st
from dfa_place_finder import build_dfa, scan_paragraph


# ----------------------------------------------------------------------
#  Build DFA once per session
# ----------------------------------------------------------------------
@st.cache_resource
def _get_dfa():
    return build_dfa()

dfa, MAX_LEN = _get_dfa()

# ----------------------------------------------------------------------
#  UI – input
# ----------------------------------------------------------------------
st.title("DFA Word / Phrase Highlighter")

paragraph = st.text_area(
    "Enter (or paste) a paragraph:",
    height=250,
    placeholder="Type your paragraph here…",
)

