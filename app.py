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

# ----------------------------------------------------------------------
#  Run DFA + show results
# ----------------------------------------------------------------------
if paragraph.strip():
    verdicts, bold_para = scan_paragraph(paragraph, dfa, MAX_LEN)

    # ------------- Tabs ---------------
    tab_verdicts, tab_para = st.tabs(["🗒️ Verdicts", "📄 Paragraph"])

    # ---- Tab 1: verdict list in a scrollable dataframe ----
    with tab_verdicts:
        df = pd.DataFrame(verdicts, columns=["Token / Phrase", "Accepted?"])
        df["Accepted?"] = df["Accepted?"].map({True: "Yes", False: "No"})
        # 350 px tall scroll box
        st.dataframe(
            df,
            use_container_width=True,
            height=350,
        )
        # optional CSV download
        csv = df.to_csv(index=False).encode()
        st.download_button(
            "Download verdicts as CSV",
            csv,
            "dfa_verdicts.csv",
            "text/csv",
        )

    # ---- Tab 2: boldfaced paragraph ----
    with tab_para:
        st.markdown(bold_para, unsafe_allow_html=True)
else:
    st.info("Enter a paragraph above and results will appear instantly.")
