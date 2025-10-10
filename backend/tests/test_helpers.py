"""
Helper functions for tests
"""

def create_test_logo_base64() -> str:
    """
    Create a valid test logo in base64 format.
    This is a 1x1 transparent PNG.
    """
    return 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='


def create_test_job_data(job_id: str, status: str = 'pending') -> dict:
    """Create test job data with customizable status"""
    return {
        'id': job_id,
        'customer_name': 'Test Company',
        'industry': 'Construction',
        'status': status,
        'progress': 0 if status == 'pending' else 100 if status == 'completed' else 50,
        'pdf_url': 'https://example.com/test.pdf' if status == 'completed' else None,
        'error_message': 'Test error' if status == 'failed' else None,
        'metadata': {
            'items': ['Sweatshirt'],
            'colors': ['Red'],
            'total_pages': 1
        },
        'created_at': '2025-10-09T10:00:00Z',
        'updated_at': '2025-10-09T10:00:00Z'
    }


def assert_valid_uuid(uuid_string: str) -> bool:
    """Validate that a string is a valid UUID"""
    import uuid
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False
