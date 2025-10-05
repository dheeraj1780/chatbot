import requests
from config import ENDPOINTS

def get_all_groups(headers):
    """Get all document groups"""
    try:
        response = requests.get(ENDPOINTS['GROUPS'], headers=headers)
        if response.status_code == 200:
            return {'success': True, 'data': response.json()}
        else:
            return {'success': False, 'error': response.json().get('detail', 'Failed to fetch groups')}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def create_group(name, description, headers):
    """Create a new document group"""
    try:
        response = requests.post(
            ENDPOINTS['GROUPS'],
            json={'name': name, 'description': description},
            headers=headers
        )
        if response.status_code == 200:
            return {'success': True, 'data': response.json()}
        else:
            return {'success': False, 'error': response.json().get('detail', 'Failed to create group')}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def upload_document(file, group_id, headers):
    """Upload a document to a group"""
    try:
        files = {'file': file}
        data = {'group_id': group_id}
        response = requests.post(
            ENDPOINTS['UPLOAD'],
            files=files,
            data=data,
            headers=headers
        )
        if response.status_code == 200:
            return {'success': True, 'data': response.json()}
        else:
            return {'success': False, 'error': response.json().get('detail', 'Failed to upload document')}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def get_group_documents(group_id, headers):
    """Get all documents in a group"""
    try:
        response = requests.get(ENDPOINTS['DOCUMENTS'](group_id), headers=headers)
        if response.status_code == 200:
            return {'success': True, 'data': response.json()}
        else:
            return {'success': False, 'error': response.json().get('detail', 'Failed to fetch documents')}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def delete_document(document_id, headers):
    """Delete a document"""
    try:
        response = requests.delete(ENDPOINTS['DELETE_DOCUMENT'](document_id), headers=headers)
        if response.status_code == 200:
            return {'success': True, 'data': response.json()}
        else:
            return {'success': False, 'error': response.json().get('detail', 'Failed to delete document')}
    except Exception as e:
        return {'success': False, 'error': str(e)}