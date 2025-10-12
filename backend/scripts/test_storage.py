# scripts/test_storage.py
"""
Standalone test for Supabase Storage
Run from anywhere: python scripts/test_storage.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

import asyncio
import httpx
from dotenv import load_dotenv

# Load .env
env_path = project_root / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"✓ Loaded .env from: {env_path}\n")
else:
    print(f"❌ .env not found at {env_path}")
    sys.exit(1)

# Get config
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
BUCKET_NAME = os.getenv('STORAGE_BUCKET_NAME', 'catalog-assets')

print("Configuration:")
print(f"  Supabase URL: {SUPABASE_URL}")
print(f"  Service Key: {SUPABASE_SERVICE_KEY[:20]}..." if SUPABASE_SERVICE_KEY else "  Service Key: NOT SET")
print(f"  Bucket: {BUCKET_NAME}")
print()

if not all([SUPABASE_URL, SUPABASE_SERVICE_KEY]):
    print("❌ Missing required environment variables!")
    sys.exit(1)


async def test_upload_http():
    """Test upload using direct HTTP request"""
    
    print("="*60)
    print("Testing Upload with Direct HTTP")
    print("="*60)
    
    test_path = "test/hello.txt"
    test_content = b"Hello, Supabase Storage!"
    
    # Construct URL
    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET_NAME}/{test_path}"
    
    print(f"\nUploading:")
    print(f"  URL: {url}")
    print(f"  Path: {test_path}")
    print(f"  Size: {len(test_content)} bytes")
    
    headers = {
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "text/plain",
        "x-upsert": "true"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                content=test_content,
                headers=headers
            )
            
            print(f"\nResponse:")
            print(f"  Status: {response.status_code}")
            print(f"  Body: {response.text[:200]}")
            
            if response.status_code in [200, 201]:
                public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{test_path}"
                print(f"\n✓ SUCCESS!")
                print(f"  Public URL: {public_url}")
                print(f"\nTry accessing: {public_url}")
                return True
            else:
                print(f"\n✗ FAILED")
                print(f"  Error: {response.text}")
                return False
                
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_upload_supabase_client():
    """Test upload using Supabase Python client"""
    
    print("\n" + "="*60)
    print("Testing Upload with Supabase Client")
    print("="*60)
    
    try:
        from supabase import create_client
        
        client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        
        test_path = "test/hello-client.txt"
        test_content = b"Hello from Supabase client!"
        
        print(f"\nUploading:")
        print(f"  Path: {test_path}")
        print(f"  Size: {len(test_content)} bytes")
        
        # Upload
        res = client.storage.from_(BUCKET_NAME).upload(
            path=test_path,
            file=test_content,
            file_options={
                "content-type": "text/plain",
                "upsert": "true"
            }
        )
        
        print(f"\nUpload response: {res}")
        
        # Get public URL
        public_url = client.storage.from_(BUCKET_NAME).get_public_url(test_path)
        
        print(f"\n✓ SUCCESS!")
        print(f"  Public URL: {public_url}")
        print(f"\nTry accessing: {public_url}")
        return True
        
    except ImportError:
        print("\n⚠️  Supabase client not installed")
        print("  Install with: pip install supabase")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        print(f"  Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_list_buckets():
    """List all available buckets"""
    
    print("\n" + "="*60)
    print("Listing Buckets")
    print("="*60)
    
    url = f"{SUPABASE_URL}/storage/v1/bucket"
    headers = {
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code == 200:
                buckets = response.json()
                print(f"\nFound {len(buckets)} bucket(s):")
                for bucket in buckets:
                    print(f"  • {bucket.get('name')} (public: {bucket.get('public', False)})")
                
                # Check if our bucket exists
                bucket_names = [b.get('name') for b in buckets]
                if BUCKET_NAME in bucket_names:
                    print(f"\n✓ Bucket '{BUCKET_NAME}' exists")
                    return True
                else:
                    print(f"\n✗ Bucket '{BUCKET_NAME}' NOT FOUND")
                    print(f"\nCreate it in Supabase Dashboard:")
                    print(f"  1. Go to: {SUPABASE_URL.replace('https://', 'https://supabase.com/dashboard/project/')}/storage/buckets")
                    print(f"  2. Click 'New bucket'")
                    print(f"  3. Name: {BUCKET_NAME}")
                    print(f"  4. Public: ON")
                    return False
            else:
                print(f"✗ Failed to list buckets: {response.status_code}")
                print(f"  Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


async def main():
    """Run all tests"""
    
    print("\n" + "="*60)
    print(" Supabase Storage Connection Test")
    print("="*60 + "\n")
    
    # Test 1: List buckets (verify bucket exists)
    bucket_exists = await test_list_buckets()
    
    if not bucket_exists:
        print("\n" + "="*60)
        print("STOPPING: Bucket doesn't exist")
        print("="*60)
        return
    
    # Test 2: Upload with HTTP
    http_success = await test_upload_http()
    
    # Test 3: Upload with Supabase client
    client_success = await test_upload_supabase_client()
    
    # Summary
    print("\n" + "="*60)
    print(" Summary")
    print("="*60)
    print(f"{'✓' if bucket_exists else '✗'} Bucket exists")
    print(f"{'✓' if http_success else '✗'} HTTP upload")
    print(f"{'✓' if client_success else '✗'} Supabase client upload")
    
    if http_success or client_success:
        print("\n🎉 At least one method works!")
        if http_success and not client_success:
            print("\n💡 Recommendation: Use StorageServiceHTTP in your app")
        elif client_success:
            print("\n💡 Recommendation: Use StorageService in your app")
    else:
        print("\n❌ Both methods failed. Check:")
        print("  1. Is SUPABASE_SERVICE_KEY correct? (not anon key)")
        print("  2. Is bucket public?")
        print("  3. Try creating a file manually in Supabase Dashboard")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted by user, exiting...")