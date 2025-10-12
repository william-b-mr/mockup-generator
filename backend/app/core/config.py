
"""
Standalone test script for n8n webhooks
No dependencies on app configuration - reads directly from .env

Run from anywhere: python scripts/test_n8n_standalone.py
"""

import asyncio
import httpx
import os
from pathlib import Path
from dotenv import load_dotenv

# Find and load .env file
def find_env_file():
    """Find .env file in project root"""
    current = Path.cwd()
    
    # Try current directory first
    if (current / '.env').exists():
        return current / '.env'
    
    # Try parent directory (if running from scripts/)
    if (current.parent / '.env').exists():
        return current.parent / '.env'
    
    # Try going up to find backend folder
    for parent in current.parents:
        env_path = parent / '.env'
        if env_path.exists():
            return env_path
    
    return None

# Load environment variables
env_file = find_env_file()
if env_file:
    load_dotenv(env_file)
    print(f"✓ Loaded .env from: {env_file}\n")
else:
    print("❌ Error: .env file not found!")
    print("Please create a .env file in the project root with:")
    print("  N8N_WEBHOOK_BASE_URL=your_n8n_url")
    print("  N8N_LOGO_PROCESSING_WEBHOOK=webhook_id_1")
    print("  N8N_PAGE_GENERATOR_WEBHOOK=webhook_id_2")
    exit(1)

# Get configuration from environment
N8N_BASE_URL = os.getenv('N8N_WEBHOOK_BASE_URL')
LOGO_WEBHOOK_ID = os.getenv('N8N_LOGO_PROCESSING_WEBHOOK')
PAGE_WEBHOOK_ID = os.getenv('N8N_PAGE_GENERATOR_WEBHOOK')

# Validate configuration
if not all([N8N_BASE_URL, LOGO_WEBHOOK_ID, PAGE_WEBHOOK_ID]):
    print("❌ Error: Missing required environment variables!")
    print("\nFound:")
    print(f"  N8N_WEBHOOK_BASE_URL: {'✓' if N8N_BASE_URL else '✗'}")
    print(f"  N8N_LOGO_PROCESSING_WEBHOOK: {'✓' if LOGO_WEBHOOK_ID else '✗'}")
    print(f"  N8N_PAGE_GENERATOR_WEBHOOK: {'✓' if PAGE_WEBHOOK_ID else '✗'}")
    exit(1)

async def test_webhook(name: str, webhook_id: str, payload: dict):
    """Test a single webhook"""
    url = f"{N8N_BASE_URL}/{webhook_id}"
    
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"{'='*60}")
    print(f"URL: {url}")
    print(f"Payload: {payload}")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"\nStatus Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✓ SUCCESS")
                try:
                    data = response.json()
                    print(f"Response: {data}")
                except:
                    print(f"Response: {response.text[:200]}")
                return True
            else:
                print(f"✗ FAILED")
                print(f"Response: {response.text[:200]}")
                return False
                
    except httpx.TimeoutException:
        print("✗ TIMEOUT - Request took longer than 10 seconds")
        return False
    except httpx.ConnectError:
        print(f"✗ CONNECTION ERROR - Cannot connect to {url}")
        print("\nPossible issues:")
        print("  1. n8n is not running")
        print("  2. Wrong URL in .env")
        print("  3. Firewall blocking connection")
        return False
    except Exception as e:
        print(f"✗ ERROR - {str(e)}")
        return False

async def main():
    """Run all webhook tests"""
    
    print("\n" + "="*60)
    print(" n8n Webhook Connection Test")
    print("="*60)
    print(f"\nBase URL: {N8N_BASE_URL}")
    print(f"Logo Webhook: {LOGO_WEBHOOK_ID}")
    print(f"Page Webhook: {PAGE_WEBHOOK_ID}")
    
    # Test Logo Processing Webhook
    logo_success = await test_webhook(
        name="Logo Processing Workflow",
        webhook_id=LOGO_WEBHOOK_ID,
        payload={
            'job_id': 'test-123',
            'logo_url': 'https://via.placeholder.com/150'
        }
    )
    
    await asyncio.sleep(1)  # Brief pause between tests
    
    # Test Page Generator Webhook
    page_success = await test_webhook(
        name="Page Generator Workflow",
        webhook_id=PAGE_WEBHOOK_ID,
        payload={
            'job_id': 'test-123',
            'item': 'Test Sweatshirt',
            'color': 'Red',
            'logo_large_url': 'https://via.placeholder.com/800',
            'logo_small_url': 'https://via.placeholder.com/300'
        }
    )
    
    # Summary
    print(f"\n{'='*60}")
    print(" Summary")
    print(f"{'='*60}")
    print(f"{'✓' if logo_success else '✗'} Logo Processing Workflow")
    print(f"{'✓' if page_success else '✗'} Page Generator Workflow")
    
    if logo_success and page_success:
        print("\n🎉 All webhooks are working!")
        return 0
    else:
        print("\n⚠️  Some webhooks failed. Check the errors above.")
        return 1

if __name__ == '__main__':
    try:
        exit_code = asyncio.run(main())
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        exit(1)