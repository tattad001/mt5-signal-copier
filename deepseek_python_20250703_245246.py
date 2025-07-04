import pytesseract
from PIL import Image
import io

async def extract_text_from_image(message):
    try:
        # Download the image
        image_bytes = await message.download_media(bytes)
        img = Image.open(io.BytesIO(image_bytes))
        
        # Preprocess image for better OCR
        img = img.convert('L')  # Grayscale
        img = img.point(lambda x: 0 if x < 128 else 255, '1')  # Binarize
        
        # Extract text
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        logging.error(f"OCR failed: {str(e)}")
        return ""