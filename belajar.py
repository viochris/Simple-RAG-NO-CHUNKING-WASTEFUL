import streamlit as st
from google import genai
from google.genai import types

def reset_state():
    st.session_state["message"] = []

if "api_key" not in st.session_state:
    st.session_state["api_key"] = ""
if "message" not in st.session_state:
    st.session_state["message"] = []
if "document" not in st.session_state:
    st.session_state["document"] = None

st.set_page_config(page_title="DocuChat AI", page_icon="📚",layout="wide" )
st.title("🤖 DocuChat: Chat with your Documents")
st.markdown(
    """
    **Unlock the knowledge inside your files.** Upload a document (PDF, DOCX, or TXT) in the sidebar and ask any question about its content.
    """
)

with st.sidebar:
    st.header("⚙️ Configuration")

    google_api_key = st.text_input("Enter your Google API Key", type="password", key="input_widget")
    st.session_state["api_key"] = google_api_key

    st.button("🔄 Reset Conversation", on_click=reset_state)

    st.divider()

    uploaded_files = st.file_uploader(
        label="Upload Knowledge Base",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload the documents you want to chat about. ONLY Supported PDF formats"
    )

    content_parts = []
    if uploaded_files:
        st.info(f"✅ {len(uploaded_files)} document(s) loaded!")
    else:
        st.warning("Please Input your File first")

if not st.session_state["api_key"]:
    st.warning("⚠️ Please enter your Google API Key in the sidebar to proceed.")

for msg in st.session_state["message"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg['content'])

# Create the chat input widget with built-in file upload capability
prompt_text = st.chat_input(placeholder="Ask a question about your documents...")

# Handling the input
if prompt_text:
    st.session_state["message"].append({"role": "human", "content": prompt_text})
    with st.chat_message("human"):
        st.markdown(prompt_text)

    try:
        client = genai.Client(api_key=st.session_state["api_key"])

        content_parts = []
        if uploaded_files:
            for uploaded_file in uploaded_files:
                content_parts.append(
                    types.Part.from_bytes(
                    data=uploaded_file.getvalue(),
                    mime_type='application/pdf',
                    )
                )

        content_parts.append(prompt_text)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=content_parts
        )
        answer = response.text
    
    except Exception as e:
        answer = f"An error occurred: {e}"

    with st.chat_message("ai"):
        st.markdown(answer)

    st.session_state["message"].append({"role": "ai", "content": answer})