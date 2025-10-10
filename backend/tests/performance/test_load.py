"""
Performance tests to ensure system handles load
"""

import pytest
import asyncio
from concurrent.futures import ThreadPoolExecutor


@pytest.mark.slow
@pytest.mark.performance
class TestPerformance:
    """Performance and load tests"""
    
    def test_concurrent_requests(self, client, sample_catalog_request):
        """
        Test system can handle multiple concurrent requests.
        This is a basic load test.
        """
        def make_request():
            return client.post('/api/catalog/generate', json=sample_catalog_request)
        
        # Execute 10 concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            responses = [f.result() for f in futures]
        
        # Verify all requests were handled
        successful_requests = [r for r in responses if r.status_code == 200]
        assert len(successful_requests) >= 8  # Allow some failures under load
    
    def test_api_response_time(self, client):
        """Test that health endpoint responds quickly"""
        import time
        
        start = time.time()
        response = client.get('/api/health')
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 0.5  # Should respond in less than 500ms

