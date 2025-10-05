import requests
from config import ENDPOINTS

def login(username, password):
    """Login user"""
    try:
        response = requests.post(
            ENDPOINTS['LOGIN'],
            json={'username': username, 'password': password}
        )
        if response.status_code == 200:
            return {'success': True, 'data': response.json()}
        else:
            return {'success': False, 'error': response.json().get('detail', 'Login failed')}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def logout(token):
    """Logout user"""
    try:
        response = requests.post(
            ENDPOINTS['LOGOUT'],
            headers={'Authorization': f'Bearer {token}'}
        )
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}