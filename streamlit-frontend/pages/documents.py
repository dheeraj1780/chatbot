import streamlit as st
import sys
sys.path.append('..')

from utils.session import init_session_state, is_authenticated, is_admin, get_headers, clear_auth
from api.document_api import get_all_groups, create_group, upload_document, get_group_documents, delete_document
from api.auth_api import logout
from utils.helpers import format_date

# Initialize session
init_session_state()

# Check authentication and admin
if not is_authenticated():
    st.warning("Please login to access this page")
    st.switch_page("app.py")
    st.stop()

if not is_admin():
    st.error("⛔ Access Denied: Admin privileges required")
    st.stop()

# Page config
st.set_page_config(page_title="Documents", page_icon="📄", layout="wide")

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
st.title("📄 Document Management")
st.markdown("Create groups and manage your documents")
st.markdown("---")

# Tabs
tab1, tab2, tab3 = st.tabs(["📁 Groups", "📤 Upload Document", "📋 View Documents"])

# Tab 1: Create Group
with tab1:
    st.markdown("### Create New Document Group")
    
    with st.form("create_group_form"):
        group_name = st.text_input("Group Name", placeholder="e.g., Technical Documents")
        group_description = st.text_area("Description", placeholder="Describe the purpose of this group...")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            submit_group = st.form_submit_button("➕ Create Group", use_container_width=True)
        
        if submit_group:
            if not group_name or not group_description:
                st.error("Please fill in all fields")
            else:
                with st.spinner("Creating group..."):
                    result = create_group(group_name, group_description, get_headers())
                    
                    if result['success']:
                        st.success(f"Group '{group_name}' created successfully!")
                        st.balloons()
                    else:
                        st.error(f"Failed to create group: {result['error']}")
    
    st.markdown("---")
    
    # List existing groups
    st.markdown("### 📚 Existing Groups")
    
    with st.spinner("Loading groups..."):
        result = get_all_groups(get_headers())
        
        if result['success']:
            groups = result['data']
            
            if len(groups) == 0:
                st.info("No groups created yet. Create your first group above!")
            else:
                for group in groups:
                    with st.expander(f"📁 {group['name']}", expanded=False):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"**Description:** {group['description']}")
                            st.markdown(f"**Created:** {format_date(group['created_at'])}")
                            st.markdown(f"**ID:** {group['id']}")
                        
                        with col2:
                            st.markdown("**Actions:**")
                            if st.button("📋 View Docs", key=f"view_{group['id']}", use_container_width=True):
                                st.session_state['selected_group_view'] = group['id']
                                st.rerun()
        else:
            st.error(f"Failed to load groups: {result['error']}")

# Tab 2: Upload Document
with tab2:
    st.markdown("### Upload Document to Group")
    
    # Get groups for dropdown
    with st.spinner("Loading groups..."):
        result = get_all_groups(get_headers())
        
        if result['success']:
            groups = result['data']
            
            if len(groups) == 0:
                st.warning("⚠️ No groups available. Please create a group first in the 'Groups' tab.")
            else:
                with st.form("upload_document_form"):
                    # Group selection
                    group_options = {group['name']: group['id'] for group in groups}
                    selected_group_name = st.selectbox("Select Group", options=list(group_options.keys()))
                    selected_group_id = group_options[selected_group_name]
                    
                    # File upload
                    uploaded_file = st.file_uploader(
                        "Choose a document",
                        type=['pdf', 'txt', 'doc', 'docx'],
                        help="Supported formats: PDF, TXT, DOC, DOCX"
                    )
                    
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        submit_upload = st.form_submit_button("📤 Upload", use_container_width=True)
                    
                    if submit_upload:
                        if not uploaded_file:
                            st.error("Please select a file to upload")
                        else:
                            with st.spinner(f"Uploading {uploaded_file.name}..."):
                                # Reset file pointer to beginning
                                uploaded_file.seek(0)
                                
                                result = upload_document(uploaded_file, selected_group_id, get_headers())
                                
                                if result['success']:
                                    st.success(f"✅ Document '{uploaded_file.name}' uploaded successfully!")
                                    st.info(f"📊 {result['data'].get('chunks_created', 'N/A')} chunks created")
                                    st.balloons()
                                else:
                                    st.error(f"❌ Failed to upload document: {result['error']}")
        else:
            st.error(f"Failed to load groups: {result['error']}")

# Tab 3: View Documents
with tab3:
    st.markdown("### View Documents by Group")
    
    # Get groups for dropdown
    with st.spinner("Loading groups..."):
        result = get_all_groups(get_headers())
        
        if result['success']:
            groups = result['data']
            
            if len(groups) == 0:
                st.warning("⚠️ No groups available.")
            else:
                # Group selection
                group_options = {f"{group['name']} (ID: {group['id']})": group['id'] for group in groups}
                selected_display = st.selectbox("Select a group to view documents", options=list(group_options.keys()))
                view_group_id = group_options[selected_display]
                
                if st.button("🔍 Load Documents", use_container_width=False):
                    st.session_state['selected_group_view'] = view_group_id
                
                # Display documents if a group is selected
                if 'selected_group_view' in st.session_state:
                    group_id = st.session_state['selected_group_view']
                    
                    st.markdown("---")
                    st.markdown("### 📄 Documents")
                    
                    with st.spinner("Loading documents..."):
                        result = get_group_documents(group_id, get_headers())
                        
                        if result['success']:
                            documents = result['data']
                            
                            if len(documents) == 0:
                                st.info("No documents in this group yet.")
                            else:
                                for doc in documents:
                                    col1, col2, col3 = st.columns([3, 2, 1])
                                    
                                    with col1:
                                        st.markdown(f"**📄 {doc['filename']}**")
                                    
                                    with col2:
                                        st.markdown(f"*{format_date(doc['uploaded_at'])}*")
                                    
                                    with col3:
                                        if st.button("🗑️", key=f"delete_{doc['id']}", help="Delete document"):
                                            with st.spinner("Deleting..."):
                                                delete_result = delete_document(doc['id'], get_headers())
                                                
                                                if delete_result['success']:
                                                    st.success("Document deleted!")
                                                    st.rerun()
                                                else:
                                                    st.error(f"Failed to delete: {delete_result['error']}")
                                    
                                    st.markdown("---")
                        else:
                            st.error(f"Failed to load documents: {result['error']}")
        else:
            st.error(f"Failed to load groups: {result['error']}")