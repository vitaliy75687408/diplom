import os
from google import genai
from google.genai import types
from PIL import Image
import io

# Get API key from environment
api_key = 'AIzaSyAPMg-fma4e4E8rt6yV9DeQbHAV5bkw-9w' 

client = genai.Client(api_key=api_key)

try:
    print("Creating hairstyle via Imagen 3... Please wait.")
    
    response = client.models.generate_images(
        model="imagen-3.0-generate-001",
        prompt="A high-quality, realistic photo of a modern men's haircut, mid fade, textured top, barber shop lighting, 4k resolution",
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio="1:1",
            output_mime_type="image/png"
        )
    )

    # Save result
    for i, output in enumerate(response.images):
        saved_path = f"style_test_{i}.png"
        output.image.save(saved_path)
        print(f"Success! Photo saved as {saved_path}")

except Exception as e:
    print(f"Something went wrong: {e}")
