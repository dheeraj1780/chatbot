import streamlit as st

def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'token' not in st.session_state:
        st.session_state.token = None
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

def is_authenticated():
    """Check if user is authenticated"""
    return st.session_state.get('authenticated', False)

def is_admin():
    """Check if user is admin"""
    user = st.session_state.get('user', {})
    return user.get('role') == 'admin'

def get_token():
    """Get authentication token"""
    return st.session_state.get('token')

def set_auth(token, user_data):
    """Set authentication data"""
    st.session_state.authenticated = True
    st.session_state.token = token
    st.session_state.user = user_data

def clear_auth():
    """Clear authentication data"""
    st.session_state.authenticated = False
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.chat_history = []

def get_headers():
    """Get authorization headers"""
    token = get_token()
    if token:
        return {'Authorization': f'Bearer {token}'}
    return {}