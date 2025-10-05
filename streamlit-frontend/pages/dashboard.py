import streamlit as st
import sys
sys.path.append('..')

from utils.session import init_session_state, is_authenticated, is_admin, get_headers, clear_auth
from api.document_api import get_all_groups
from api.auth_api import logout

# Initialize session
init_session_state()

# Check authentication
if not is_authenticated():
    st.warning("Please login to access this page")
    st.switch_page("app.py")
    st.stop()

# Page config
st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

# Sidebar
with st.sidebar:
    st.markdown("### 👤 User Info")
    user = st.session_state.user
    st.info(f"**Username:** {user['username']}\n\n**Role:** {user['role'].title()}")
    
    st.markdown("---")
    
    if st.button("🚪 Logout", use_container_width=True):
        logout(st.session_state.token)
        clear_auth()
        st.switch_page("app.py")

# Main content
st.title("📊 Dashboard")
st.markdown("---")

# Fetch groups
with st.spinner("Loading dashboard..."):
    result = get_all_groups(get_headers())
    
    if result['success']:
        groups = result['data']
        
        # Stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📁 Document Groups", len(groups))
        
        with col2:
            st.metric("👤 Account Type", user['role'].title())
        
        with col3:
            st.metric("✅ Status", "Active")
        
        with col4:
            total_docs = sum(1 for _ in groups)  # Placeholder
            st.metric("📄 Total Access", len(groups))
        
        st.markdown("---")
        
        # Quick Actions
        st.markdown("### 🚀 Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💬 Start Chat", use_container_width=True):
                st.switch_page("pages/chat.py")
        
        with col2:
            if is_admin():
                if st.button("📤 Upload Document", use_container_width=True):
                    st.switch_page("pages/documents.py")
            else:
                st.button("📖 View Groups", use_container_width=True, disabled=True)
        
        with col3:
            if is_admin():
                if st.button("📁 Manage Groups", use_container_width=True):
                    st.switch_page("pages/documents.py")
            else:
                st.button("🔒 Admin Only", use_container_width=True, disabled=True)
        
        st.markdown("---")
        
        # Available Groups
        st.markdown("### 📚 Available Document Groups")
        
        if len(groups) == 0:
            st.info("No document groups available yet.")
        else:
            for group in groups:
                with st.expander(f"📁 {group['name']}", expanded=False):
                    st.markdown(f"**Description:** {group['description']}")
                    st.markdown(f"**Created:** {group['created_at']}")
                    st.markdown(f"**Group ID:** {group['id']}")
        
    else:
        st.error(f"Failed to load dashboard: {result['error']}")

# Footer
st.markdown("---")
st.markdown("*💡 Use the chat page to ask questions about your documents*")