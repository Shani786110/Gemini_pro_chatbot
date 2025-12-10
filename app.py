import os
import streamlit as st
from google import genai
from google.genai import types # Import 'types' to define config

# --- 1. Streamlit Page Configuration ---
st.set_page_config(
    page_title="Pro-Level Gemini Chatbot", 
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("💡 Pro-Level Gemini Chatbot")
st.caption("🚀 Powered by Google Gemini 2.5 Flash")
st.markdown("---")

# --- 2. Shared Variables (Moved outside cached function) ---
# Model selection ko bahar nikala (Error 1 fix)
st.sidebar.markdown("### Model Configuration")
model_name = st.sidebar.selectbox("Select Model:", ["gemini-2.5-flash", "gemini-2.5-pro"])

# System Instruction (Chat context)
system_prompt = (
    "You are a highly professional, helpful, and concise AI assistant built by a pro-level developer. "
    "Your primary goal is to provide accurate and quick information while maintaining context from the conversation history."
)
st.sidebar.markdown(f"**Model Used:** {model_name}")
st.sidebar.markdown("---")

# --- 3. API Key aur Client Initialization ---
def initialize_gemini_client():
    # ... (code jaisa tha, waisa hi theek hai) ...
    API_KEY = None
    try:
        API_KEY = st.secrets["GEMINI_API_KEY"]
    except KeyError:
        API_KEY = os.getenv("GEMINI_API_KEY")

    if not API_KEY:
        st.error("🚨 Gemini API Key nahi mili.")
        st.stop()
    
    try:
        client = genai.Client(api_key=API_KEY)
        return client
    except Exception as e:
        st.error(f"❌ Gemini Client initialize nahi ho paya. Error: {e}")
        st.stop()

client = initialize_gemini_client()


# --- 4. Chat Session Creation (Cached Resource) ---
# Ab is function mein koi widget nahi hai.
@st.cache_resource
def create_chat_session(_client, current_model, system_prompt_text): 
    """
    Chat session ko create karta hai, system prompt ko config mein set karta hai (Error 2 fix).
    """
    # API Update Fix: System Instruction ko configuration object mein daalna
    config = types.GenerateContentConfig(
        system_instruction=system_prompt_text
    )

    return _client.chats.create(
        model=current_model,
        config=config # 'system_instruction' ki jagah 'config' use kiya
    )

# --- 5. State Management and Execution ---

# Chat session ko create ya retrieve karna
if "chat_session" not in st.session_state:
    # Ab function ko model_name aur system_prompt dono bheje jayenge.
    st.session_state["chat_session"] = create_chat_session(client, model_name, system_prompt)

# Chat History aur baaki logic (Same as before)
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

for message in st.session_state["chat_history"]:
    with st.chat_message(message["role"]):
        st.markdown(message["text"])

if prompt := st.chat_input("Ask Gemini Pro..."):
    
    st.session_state["chat_history"].append({"role": "user", "text": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🤖 Thinking..."):
            try:
                response = st.session_state["chat_session"].send_message(prompt)
                st.markdown(response.text)
                st.session_state["chat_history"].append({"role": "assistant", "text": response.text})
            
            except Exception as e:
                error_message = f"🛑 i apologize, for some error: {e}"
                st.error(error_message)
                st.session_state["chat_history"].append({"role": "assistant", "text": "App error. Please try again."})

# Clear History Button
if st.sidebar.button("🧹 Clear Chat History"):
    st.session_state["chat_history"] = []
    st.session_state["chat_session"] = create_chat_session(client, model_name, system_prompt)
    st.rerun() 

st.sidebar.markdown("---")
st.sidebar.caption(f"Total messages in session: {len(st.session_state['chat_history'])}")