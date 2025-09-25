from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from typing import Optional, List
import asyncio
from supabase import create_client, Client
import google.generativeai as genai
from PIL import Image
import io
import base64
import uuid

app = FastAPI(title="Catalog Generator API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables (create a .env file)
SUPABASE_URL = os.getenv("SUPABASE_URL", "your-supabase-url")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "your-supabase-key")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "your-google-api-key")

# Initialize clients
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GOOGLE_API_KEY)

# Predefined industries
INDUSTRIES = [
    "Tecnologia", "Moda", "Alimentação", "Saúde", "Automóveis", 
    "Imóveis", "Educação", "Turismo", "Esportes", "Beleza"
]

@app.get("/")
async def root():
    return {"message": "Catalog Generator API"}

@app.get("/industries")
async def get_industries():
    """Get list of available industries"""
    return {"industries": INDUSTRIES}

@app.get("/templates")
async def get_templates(industry: Optional[str] = None):
    """Get templates, optionally filtered by industry"""
    try:
        if industry:
            # Filter templates by industry (you'll need to add industry field to your schema)
            response = supabase.table("templates").select("*").eq("industry", industry).execute()
        else:
            response = supabase.table("templates").select("*").execute()
        
        return {"templates": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-logo")
async def upload_logo(file: UploadFile = File(...)):
    """Upload logo to Supabase storage"""
    try:
        # Generate unique filename
        file_extension = file.filename.split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        # Upload to Supabase storage
        file_content = await file.read()
        
        response = supabase.storage.from_("logos").upload(
            unique_filename, 
            file_content,
            {"content-type": file.content_type}
        )
        
        if response.status_code == 200:
            # Get public URL
            public_url = supabase.storage.from_("logos").get_public_url(unique_filename)
            return {"url": public_url, "filename": unique_filename}
        else:
            raise HTTPException(status_code=400, detail="Upload failed")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-catalog")
async def generate_catalog(
    nome_empresa: str = Form(...),
    cores: str = Form(...),
    logo_claro_url: Optional[str] = Form(None),
    logo_escuro_url: Optional[str] = Form(None),
    mesmo_logo: bool = Form(False),
    tipo_catalogo: str = Form(...),  # "completo" or "personalizado"
    industry: Optional[str] = Form(None),
    selected_items: Optional[str] = Form(None)  # JSON string of selected item IDs
):
    """Generate catalog with AI-overlayed logos"""
    try:
        # Get templates based on catalog type
        if tipo_catalogo == "completo" and industry:
            templates_response = supabase.table("templates").select("*").eq("industry", industry).execute()
        elif tipo_catalogo == "personalizado" and selected_items:
            import json
            item_ids = json.loads(selected_items)
            templates_response = supabase.table("templates").select("*").in_("id", item_ids).execute()
        else:
            raise HTTPException(status_code=400, detail="Invalid parameters")
        
        templates = templates_response.data
        generated_images = []
        
        # Process each template
        for template in templates:
            # Determine which logo to use based on background
            logo_url = logo_claro_url if template['fundo'] == 'claro' else logo_escuro_url
            if mesmo_logo and logo_claro_url:
                logo_url = logo_claro_url
                
            if not logo_url:
                continue
                
            # Generate image with Gemini (placeholder - you'll need to implement the actual overlay logic)
            overlayed_image_url = await overlay_logo_with_gemini(
                template['template'], 
                logo_url, 
                nome_empresa, 
                cores
            )
            
            generated_images.append({
                "item": template['item'],
                "original_template": template['template'],
                "generated_image": overlayed_image_url
            })
        
        return {"generated_images": generated_images}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def overlay_logo_with_gemini(template_url: str, logo_url: str, company_name: str, colors: str):
    """
    Use Gemini to overlay logo on template
    This is a placeholder - you'll need to implement the actual image processing
    """
    try:
        ##client = genai.Client()
        
        prompt = f"""
        Overlay the logo from {logo_url} onto the template image at {template_url}.
        
        Position the logo appropriately on the product template while maintaining good visual balance.
        """
        
        # Placeholder return - implement actual Gemini image generation here
        return template_url
        
    except Exception as e:
        print(f"Error in Gemini processing: {e}")
        return template_url

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)