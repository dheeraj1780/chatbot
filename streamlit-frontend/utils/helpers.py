from datetime import datetime

def format_date(date_string):
    """Format ISO date string to readable format"""
    try:
        dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return dt.strftime('%B %d, %Y at %I:%M %p')
    except:
        return date_string

def truncate_text(text, max_length=100):
    """Truncate text to maximum length"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + '...'

def format_file_size(bytes_size):
    """Format bytes to human readable size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"