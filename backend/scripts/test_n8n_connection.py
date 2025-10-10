'''Script to test n8n webhook connectivity'''
import asyncio
import httpx
from app.core.config import settings

async def test_webhooks():
    webhooks = {
        'logo_processing': settings.N8N_LOGO_PROCESSING_WEBHOOK,
        'page_generator': settings.N8N_PAGE_GENERATOR_WEBHOOK,
        'pdf_assembly': settings.N8N_PDF_ASSEMBLY_WEBHOOK
    }
    
    for name, webhook_id in webhooks.items():
        url = f"{settings.N8N_WEBHOOK_BASE_URL}/{webhook_id}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json={'test': True}, timeout=10)
                print(f"✓ {name}: {response.status_code}")
        except Exception as e:
            print(f"✗ {name}: {e}")

if __name__ == '__main__':
    asyncio.run(test_webhooks())