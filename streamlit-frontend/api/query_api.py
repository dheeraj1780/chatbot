import requests
from config import ENDPOINTS

def ask_question(query, k=5, headers=None):
    """Ask a question to the RAG system"""
    try:
        response = requests.post(
            ENDPOINTS['ASK'],
            json={'query': query, 'k': k},
            headers=headers
        )
        if response.status_code == 200:
            return {'success': True, 'data': response.json()}
        else:
            return {'success': False, 'error': response.json().get('detail', 'Failed to get answer')}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def search_in_group(group_id, query, k=5, headers=None):
    """Search in a specific group"""
    try:
        response = requests.get(
            ENDPOINTS['SEARCH_IN_GROUP'](group_id),
            params={'query': query, 'k': k},
            headers=headers
        )
        if response.status_code == 200:
            return {'success': True, 'data': response.json()}
        else:
            return {'success': False, 'error': response.json().get('detail', 'Failed to search')}
    except Exception as e:
        return {'success': False, 'error': str(e)}