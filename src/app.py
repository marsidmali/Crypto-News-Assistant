import streamlit as st
import time
from scraper import TradingViewScraper
from rag import RAGSystem


# Initialize the app
@st.cache_resource
def initialize_app():
    scraper = TradingViewScraper()
    df = scraper.initialize_scrapper()
    rag_system = RAGSystem(df)
    rag_system.initialize_rag()
    return rag_system

# Maintain chat state in session
if "messages" not in st.session_state:
    st.session_state.messages = []
if "rag_system" not in st.session_state:
    st.session_state.rag_system = None
if "initialized" not in st.session_state:
    st.session_state.initialized = False
if "generating" not in st.session_state:
    st.session_state.generating = False

st.set_page_config(page_title="Crypto News Assistant", page_icon="📈")

if not st.session_state.messages:
    st.markdown(
        """
        <div style="text-align: center;">
            <h1>Crypto News Assistant 🤖</h1>
            <p>I analyze crypto trends and news to provide insights.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=False)

# Single input box at the bottom
user_input = st.chat_input("Ask about crypto news or trends...", key="chat_input")

# Handle user input
if user_input:
    st.session_state.should_stop = False
    st.session_state.generating = True

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input, unsafe_allow_html=False)

    # Initialize RAG system if it's the first query
    if not st.session_state.initialized:
        with st.spinner("Initializing the assistant..."):
            st.session_state.rag_system = initialize_app(df)
            st.session_state.initialized = True
            time.sleep(2)

    # Generate and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            response = st.session_state.rag_system.query(user_input).strip()  # Strip spaces

        placeholder = st.empty()
        full_response = ""

        for token in response.split(" "):
            if st.session_state.should_stop:
                break
            full_response += token + " "
            placeholder.markdown(full_response, unsafe_allow_html=False)
            time.sleep(0.05)

        # Finalize the response
        placeholder.markdown(full_response, unsafe_allow_html=False)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

    st.session_state.generating = False
