import pandas as pd
import streamlit as st
import re
import time
from dfa_place_finder import build_dfa, scan_paragraph

# Page configuration
st.set_page_config(
    page_title="DFA Highlighter Tool",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        font-size: 16px;
    }
    .app-container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .verdict-positive {
        color: #28a745;
        font-weight: bold;
    }
    .verdict-negative {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------- 
#  Parse custom phrases function
# ---------------------------------------------------------------------- 
def parse_custom_phrases(phrases_text):
    """Parse custom phrases from text input."""
    if not phrases_text.strip():
        return None
    # Split by comma or newline and strip whitespace
    phrases = [p.strip() for p in re.split(r'[,\n]+', phrases_text) if p.strip()]
    return phrases

# ---------------------------------------------------------------------- 
#  Build DFA once per session with custom phrases support
# ---------------------------------------------------------------------- 
@st.cache_resource(experimental_allow_widgets=True)
def _get_dfa(_custom_phrases=None, _cache_key=None):
    """Build DFA with optional custom phrases.
    The _cache_key parameter helps invalidate the cache when custom phrases change."""
    with st.spinner("Initializing DFA engine..."):
        return build_dfa(_custom_phrases)

# Sidebar for settings
with st.sidebar:
    st.markdown("### About This Tool")
    st.info("""
    This tool highlights words or phrases based on a DFA (Deterministic Finite Automaton).
    
    **How to use:**
    1. Enter text in the input area
    2. Optionally add custom phrases to be highlighted
    3. View the results in the tabs below
    4. Download results as needed
    """)
    
    st.markdown("### Settings")
    show_statistics = st.checkbox("Show statistics", value=True)
    highlight_color = st.color_picker("Highlight color", "#d1ffd1")
    
    # Custom phrases section
    st.markdown("### Custom Phrases")
    custom_phrases_text = st.text_area(
        "Enter custom phrases (comma or line separated):",
        placeholder="New York, Los Angeles, Chicago, etc.",
        height=150
    )
    
    use_custom = st.checkbox("Use custom phrases instead of default", value=False)
    
    if st.button("Apply Phrases"):
        if use_custom:
            st.session_state.custom_phrases = parse_custom_phrases(custom_phrases_text)
            st.session_state.use_custom_phrases = True
        else:
            st.session_state.use_custom_phrases = False
            st.session_state.custom_phrases = None
        
        # Clear the cached DFA and force a rebuild
        st.session_state.rebuild_dfa = True
        # Add a unique timestamp to invalidate cache
        st.session_state.cache_timestamp = time.time()
        st.rerun()  # Updated from st.experimental_rerun()

# Initialize session state variables
if 'rebuild_dfa' not in st.session_state:
    st.session_state.rebuild_dfa = False
if 'use_custom_phrases' not in st.session_state:
    st.session_state.use_custom_phrases = False
if 'custom_phrases' not in st.session_state:
    st.session_state.custom_phrases = None

# Main content area
st.markdown("<h1 class='main-title'>DFA Word/Phrase Highlighter</h1>", unsafe_allow_html=True)

# Initialize DFA with progress indication
with st.spinner("Loading DFA engine..."):
    # Determine which phrases to use
    phrases_to_use = st.session_state.custom_phrases if st.session_state.use_custom_phrases else None
    
    # Reset the rebuild flag and generate a unique cache key if needed
    import time
    cache_key = None
    if st.session_state.rebuild_dfa:
        st.session_state.rebuild_dfa = False
        # Force cache invalidation by adding timestamp to key
        cache_key = str(time.time())
    
    # Call get_dfa with the appropriate cache key
    dfa, MAX_LEN = _get_dfa(phrases_to_use, _cache_key=cache_key)
    
    st.success("DFA engine ready!")

# Add indicator for custom phrases
if st.session_state.use_custom_phrases and st.session_state.custom_phrases:
    st.info(f"Using {len(st.session_state.custom_phrases)} custom phrases")

# ---------------------------------------------------------------------- 
#  UI – input area
# ---------------------------------------------------------------------- 
st.markdown("<div class='app-container'>", unsafe_allow_html=True)

# Text input area - simplified, no columns needed
paragraph = st.text_area(
    "Enter (or paste) a paragraph:",
    height=250,
    placeholder="Type your paragraph here...",
)

# ---------------------------------------------------------------------- 
#  Run DFA + show results 
# ---------------------------------------------------------------------- 
if paragraph.strip():
    verdicts, bold_para = scan_paragraph(paragraph, dfa, MAX_LEN)
    
    # Update highlight color in the bold paragraph
    bold_para = bold_para.replace(
        'background-color: #d1ffd1;', 
        f'background-color: {highlight_color};'
    )
    
    # Statistics section
    if show_statistics:
        st.markdown("### Summary")
        col1, col2, col3 = st.columns(3)
        
        total_tokens = len(verdicts)
        accepted_tokens = sum(1 for _, accepted in verdicts if accepted)
        
        with col1:
            st.metric("Total Tokens", total_tokens)
        with col2:
            st.metric("Accepted Tokens", accepted_tokens)
        with col3:
            if total_tokens > 0:
                acceptance_rate = round((accepted_tokens / total_tokens) * 100, 1)
                st.metric("Acceptance Rate", f"{acceptance_rate}%")
            else:
                st.metric("Acceptance Rate", "0%")
    
    # ------------- Tabs ---------------
    tab_para, tab_verdicts = st.tabs(["📄 Highlighted Text", "🗒️ Detailed Results"])
    
    # ---- Tab 1: highlighted paragraph ----
    with tab_para:
        st.markdown(bold_para, unsafe_allow_html=True)
        
        # Download button
        st.markdown("##### Actions")
        st.download_button(
            "📥 Download as HTML",
            bold_para,
            "highlighted_text.html",
            "text/html",
        )
    
    # ---- Tab 2: verdict list in a scrollable dataframe ----
    with tab_verdicts:
        # Create a dataframe
        df = pd.DataFrame(verdicts, columns=["Token / Phrase", "Accepted?"])
        
        # Convert boolean values to Yes/No
        df["Accepted?"] = df["Accepted?"].map({True: "Yes", False: "No"})
        
        # Display the dataframe
        st.dataframe(
            df,
            use_container_width=True,
            height=350,
        )
        
        # Export options
        col1, col2 = st.columns(2)
        with col1:
            csv = df.to_csv(index=False).encode()
            st.download_button(
                "📥 Download as CSV",
                csv,
                "dfa_verdicts.csv",
                "text/csv",
            )
        with col2:
            # Add Excel export option
            try:
                import io
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='DFA Results')
                excel_data = buffer.getvalue()
                
                st.download_button(
                    "📥 Download as Excel",
                    excel_data,
                    "dfa_verdicts.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            except Exception as e:
                st.warning(f"Excel export not available: {e}")
else:
    st.info("Enter a paragraph above and results will appear instantly.")

st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("DFA Word/Phrase Highlighter Tool | Made with Streamlit")