import streamlit as st
from config import PAGE_CONFIG
from utils.session import init_session_state, is_authenticated, clear_auth, set_auth
from api.auth_api import login, logout

# Page configuration
st.set_page_config(**PAGE_CONFIG)

# Initialize session state
init_session_state()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin: 1rem 0;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

def login_page():
    """Login page"""
    st.markdown('<div class="main-header">🤖 RAG Chatbot</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Sign In")
        st.markdown("Enter your credentials to access the system")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit = st.form_submit_button("Sign In", use_container_width=True)
            
            if submit:
                if not username or not password:
                    st.error("Please enter both username and password")
                else:
                    with st.spinner("Logging in..."):
                        result = login(username, password)
                        
                        if result['success']:
                            data = result['data']
                            user_data = {
                                'id': data['user_id'],
                                'username': username,
                                'role': data['role']
                            }
                            set_auth(data['access_token'], user_data)
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error(f"Login failed: {result['error']}")

def main_page():
    """Main page after login"""
    # Sidebar
    with st.sidebar:
        st.markdown("### 👤 User Info")
        user = st.session_state.user
        st.info(f"**Username:** {user['username']}\n\n**Role:** {user['role'].title()}")
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            logout(st.session_state.token)
            clear_auth()
            st.rerun()
    
    # Main content
    st.markdown('<div class="main-header">Welcome to RAG Chatbot! 🤖</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📊 Dashboard")
        st.info("View your dashboard and statistics")
        if st.button("Go to Dashboard", key="dash", use_container_width=True):
            st.switch_page("pages/dashboard.py")
    
    with col2:
        st.markdown("### 💬 Chat")
        st.info("Ask questions about your documents")
        if st.button("Start Chatting", key="chat", use_container_width=True):
            st.switch_page("pages/chat.py")
    
    with col3:
        if st.session_state.user['role'] == 'admin':
            st.markdown("### 📄 Documents")
            st.info("Manage documents and groups")
            if st.button("Manage Documents", key="docs", use_container_width=True):
                st.switch_page("pages/documents.py")
        else:
            st.markdown("### ℹ️ Info")
            st.info("Contact admin for document access")
    
    # Features section
    st.markdown("---")
    st.markdown("## 🌟 Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **For All Users:**
        - 💬 Interactive chat interface
        - 🔍 Intelligent document search
        - 📚 Access to knowledge base
        - 🎯 Accurate AI responses
        """)
    
    with col2:
        if st.session_state.user['role'] == 'admin':
            st.markdown("""
            **Admin Features:**
            - 📁 Create document groups
            - 📤 Upload documents
            - 🗑️ Delete documents
            - 👥 Manage access
            """)
        else:
            st.markdown("""
            **Getting Started:**
            - Navigate to Chat page
            - Ask any question
            - Get instant answers
            - View sources
            """)

# Main app logic
if not is_authenticated():
    login_page()
else:
    main_page()