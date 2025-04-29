from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from PIL import Image, UnidentifiedImageError
import pytesseract
import io
import re
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


app = FastAPI()

# Optional: Uncomment if using Windows and tesseract is not in PATH
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    try:
        # Read image file
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        text = pytesseract.image_to_string(image)

        print("Extracted Text:")
        print(text)

        # Sample regex pattern
        pattern = re.compile(r'(HB ESTIMATION|PCV.*?)\s+(\d+\.\d+)\s+([a-zA-Z%/]+)\s+\(?(\d+\.\d+)-(\d+\.\d+)\)?')
        
        results = []
        for match in pattern.finditer(text):
            test_name, test_value, test_unit, min_range, max_range = match.groups()
            test_value = float(test_value)
            min_val = float(min_range)
            max_val = float(max_range)

            results.append({
                "test_name": test_name.strip(),
                "test_value": str(test_value),
                "bio_reference_range": f"{min_range}-{max_range}",
                "test_unit": test_unit.strip(),
                "lab_test_out_of_range": not (min_val <= test_value <= max_val)
            })

        return JSONResponse(content={
            "is_success": True,
            "data": results
        })

    except UnidentifiedImageError:
        return JSONResponse(status_code=400, content={"error": "Invalid image file format."})

    except Exception as e:
        print("Error:", str(e))  # Print error to console
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "details": str(e)})
