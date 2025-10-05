import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')

# API Endpoints
ENDPOINTS = {
    'LOGIN': f'{API_BASE_URL}/api/auth/login',
    'LOGOUT': f'{API_BASE_URL}/api/auth/logout',
    'GROUPS': f'{API_BASE_URL}/api/documents/groups',
    'UPLOAD': f'{API_BASE_URL}/api/documents/upload',
    'DOCUMENTS': lambda group_id: f'{API_BASE_URL}/api/documents/groups/{group_id}/documents',
    'DELETE_DOCUMENT': lambda doc_id: f'{API_BASE_URL}/api/documents/documents/{doc_id}',
    'ASK': f'{API_BASE_URL}/api/query/ask',
    'SEARCH_IN_GROUP': lambda group_id: f'{API_BASE_URL}/api/query/groups/{group_id}/search',
}

# Page Configuration
PAGE_CONFIG = {
    'page_title': 'RAG Chatbot',
    'page_icon': '🤖',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}