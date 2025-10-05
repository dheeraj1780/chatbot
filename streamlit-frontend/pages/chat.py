import streamlit as st
import sys
sys.path.append('..')

from utils.session import init_session_state, is_authenticated, get_headers, clear_auth
from api.query_api import ask_question
from api.auth_api import logout

# Initialize session
init_session_state()

# Check authentication
if not is_authenticated():
    st.warning("Please login to access this page")
    st.switch_page("app.py")
    st.stop()

# Page config
st.set_page_config(page_title="Chat", page_icon="💬", layout="wide")

# Sidebar
with st.sidebar:
    st.markdown("### 👤 User Info")
    user = st.session_state.user
    st.info(f"**Username:** {user['username']}\n\n**Role:** {user['role'].title()}")
    
    st.markdown("---")
    
    st.markdown("### ⚙️ Chat Settings")
    k_value = st.slider("Number of chunks to retrieve", 1, 10, 5)
    
    st.markdown("---")
    
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()
    
    st.markdown("---")
    
    if st.button("🚪 Logout", use_container_width=True):
        logout(st.session_state.token)
        clear_auth()
        st.switch_page("app.py")

# Main content
st.title("💬 Chat Assistant")
st.markdown("Ask me anything about your documents!")
st.markdown("---")

# Chat container
chat_container = st.container()

with chat_container:
    if len(st.session_state.chat_history) == 0:
        st.info("👋 Hello! I'm your AI assistant. Ask me any question about your documents to get started.")
    else:
        for message in st.session_state.chat_history:
            if message['type'] == 'user':
                with st.chat_message("user", avatar="👤"):
                    st.markdown(message['content'])
            elif message['type'] == 'assistant':
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(message['content'])
                    if 'metadata' in message and message['metadata']:
                        with st.expander("📊 Response Details"):
                            st.markdown(f"**Source Group:** {message['metadata'].get('group_used', 'N/A')}")
                            st.markdown(f"**Chunks Found:** {message['metadata'].get('chunks_found', 'N/A')}")
            elif message['type'] == 'error':
                with st.chat_message("assistant", avatar="⚠️"):
                    st.error(message['content'])

# Chat input
user_input = st.chat_input("Type your question here...")

if user_input:
    # Add user message
    st.session_state.chat_history.append({
        'type': 'user',
        'content': user_input
    })
    
    # Get response
    with st.spinner("Thinking..."):
        result = ask_question(user_input, k=k_value, headers=get_headers())
        
        if result['success']:
            data = result['data']
            st.session_state.chat_history.append({
                'type': 'assistant',
                'content': data['answer'],
                'metadata': {
                    'group_used': data.get('group_used'),
                    'chunks_found': data.get('chunks_found')
                }
            })
        else:
            st.session_state.chat_history.append({
                'type': 'error',
                'content': f"Error: {result['error']}"
            })
    
    st.rerun()

# Tips
with st.expander("💡 Tips for better results"):
    st.markdown("""
    - Be specific with your questions
    - Ask one question at a time
    - Use clear and concise language
    - Refer to specific topics or documents when possible
    - Adjust the number of chunks if needed for more context
    """)