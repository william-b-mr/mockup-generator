"""
Test script for AI hero image generation
Tests the flow: template image + clothing pages -> AI-generated hero image

Directory structure:
├── test_image_generation.py (this file)
└── assets/
    ├── template.jpg (industry template image)
    ├── clothing_1.png (generated clothing page 1)
    ├── clothing_2.png (generated clothing page 2)
    └── ... (more clothing pages)
"""

import os
import base64
from openai import OpenAI
import requests
from pathlib import Path

# Initialize OpenAI client
# Get API key from environment or prompt user
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ OPENAI_API_KEY environment variable not set!")
    print("\nOptions:")
    print("1. Set it in your terminal: export OPENAI_API_KEY='your-key-here'")
    print("2. Add it to a .env file")
    print("3. Enter it now (not recommended for production)\n")
    
    api_key = input("Enter your OpenAI API key (or press Ctrl+C to exit): ").strip()
    
    if not api_key:
        print("❌ No API key provided. Exiting.")
        exit(1)

client = OpenAI(api_key=api_key)

# Configuration
ASSETS_DIR = Path("assets")
TEMPLATE_IMAGE = ASSETS_DIR / "template.jpg"
OUTPUT_IMAGE = "generated_hero.png"


def encode_image(image_path: Path) -> str:
    """Encode image to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def get_clothing_images() -> list[Path]:
    """Get all clothing images from assets folder"""
    clothing_files = []
    for ext in ['*.png', '*.jpg', '*.jpeg']:
        clothing_files.extend(ASSETS_DIR.glob(ext))
    
    # Exclude template image
    clothing_files = [f for f in clothing_files if f.name != TEMPLATE_IMAGE.name]
    
    # Limit to first 5 images for testing
    return clothing_files[:5]


def analyze_images_and_create_prompt(template_b64: str, clothing_images_b64: list[str]) -> str:
    """
    Use GPT-4 Vision to analyze template and clothing images,
    then create a detailed prompt for DALL-E
    """
    
    print("🔍 Step 1: Analyzing images with GPT-4 Vision...")
    
    # Build the analysis prompt
    analysis_prompt = """You are helping create a professional catalog cover image.

ANALYZE the template image showing people in a professional setting and the reference clothing images provided.

CREATE a detailed DALL-E prompt that describes:
1. The setting, composition, and atmosphere from the template image
2. The specific clothing items from the reference images that should replace what people are wearing
3. How to maintain professional quality and natural appearance

Your response should be ONLY the DALL-E prompt text, nothing else. Make it detailed and specific."""

    # Build messages with all images
    content = [
        {"type": "text", "text": analysis_prompt},
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{template_b64}",
                "detail": "high"
            }
        }
    ]
    
    # Add clothing reference images
    for idx, clothing_b64 in enumerate(clothing_images_b64):
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{clothing_b64}",
                "detail": "high"
            }
        })
    
    # Call GPT-4 Vision
    response = client.chat.completions.create(
        model="gpt-4o",  # or "gpt-4-turbo" or "gpt-4o-mini"
        messages=[
            {
                "role": "user",
                "content": content
            }
        ],
        max_tokens=500
    )
    
    dalle_prompt = response.choices[0].message.content
    print(f"✅ Generated DALL-E prompt:\n{dalle_prompt}\n")
    
    return dalle_prompt


def generate_hero_image(dalle_prompt: str) -> str:
    """
    Generate hero image using DALL-E 3
    Returns: URL of generated image
    """
    
    print("🎨 Step 2: Generating image with DALL-E 3...")
    
    response = client.images.generate(
        model="dall-e-3",
        prompt=dalle_prompt,
        size="1792x1024",  # Landscape format, good for hero images
        quality="hd",
        n=1
    )
    
    image_url = response.data[0].url
    print(f"✅ Image generated: {image_url}\n")
    
    return image_url


def download_image(url: str, output_path: str):
    """Download image from URL and save locally"""
    
    print(f"💾 Step 3: Downloading image to {output_path}...")
    
    response = requests.get(url)
    response.raise_for_status()
    
    with open(output_path, 'wb') as f:
        f.write(response.content)
    
    print(f"✅ Image saved successfully!\n")


def main():
    print("=" * 60)
    print("AI Hero Image Generation Test")
    print("=" * 60 + "\n")
    
    # Verify assets directory exists
    if not ASSETS_DIR.exists():
        print(f"❌ Error: '{ASSETS_DIR}' directory not found!")
        print("Please create an 'assets' folder and add:")
        print("  - template.jpg (your industry template)")
        print("  - clothing_*.png (your clothing pages)")
        return
    
    # Verify template exists
    if not TEMPLATE_IMAGE.exists():
        print(f"❌ Error: Template image not found at {TEMPLATE_IMAGE}")
        return
    
    # Get clothing images
    clothing_images = get_clothing_images()
    if not clothing_images:
        print("❌ Error: No clothing images found in assets folder!")
        return
    
    print(f"📁 Found template: {TEMPLATE_IMAGE.name}")
    print(f"📁 Found {len(clothing_images)} clothing images:")
    for img in clothing_images:
        print(f"   - {img.name}")
    print()
    
    try:
        # Encode all images
        print("📦 Encoding images...")
        template_b64 = encode_image(TEMPLATE_IMAGE)
        clothing_b64_list = [encode_image(img) for img in clothing_images]
        print("✅ Images encoded\n")
        
        # Step 1: Analyze and create prompt
        dalle_prompt = analyze_images_and_create_prompt(template_b64, clothing_b64_list)
        
        # Step 2: Generate image with DALL-E
        image_url = generate_hero_image(dalle_prompt)
        
        # Step 3: Download generated image
        download_image(image_url, OUTPUT_IMAGE)
        
        print("=" * 60)
        print("🎉 SUCCESS! Hero image generated and saved.")
        print(f"📄 Output file: {OUTPUT_IMAGE}")
        print(f"🔗 URL: {image_url}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()