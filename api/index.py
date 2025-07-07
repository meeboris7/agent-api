from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl
import httpx
from io import BytesIO
from docx import Document
from PyPDF2 import PdfReader
from mangum import Mangum  

app = FastAPI()

# ... rest of your code ...
# --- Request Body Model ---
class DocumentParseRequest(BaseModel):
    url: HttpUrl

# --- Helper Functions for Text Extraction ---

async def extract_text_from_pdf(file_content: BytesIO) -> str:
    """Extracts text from a PDF file."""
    try:
        reader = PdfReader(file_content)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {e}")

async def extract_text_from_docx(file_content: BytesIO) -> str:
    """Extracts text from a DOCX file."""
    try:
        document = Document(file_content)
        text = "\n".join([paragraph.text for paragraph in document.paragraphs])
        return text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing DOCX: {e}")

# --- API Endpoint ---

@app.post("/parse_document/")
async def parse_document(request: DocumentParseRequest):
    """
    Parses a document from a given URL and extracts its text content.
    Supports PDF (.pdf) and DOCX (.docx) file formats.
    """
    file_url = str(request.url) # Convert HttpUrl to string for httpx
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(file_url, follow_redirects=True)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        except httpx.RequestError as e:
            raise HTTPException(status_code=400, detail=f"Could not download file from URL: {e}")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"HTTP error downloading file: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred during download: {e}")

    # Determine file type based on content-type header or URL extension
    content_type = response.headers.get("content-type", "").lower()
    
    # Use BytesIO to treat the downloaded content as a file-like object
    file_content = BytesIO(response.content)

    extracted_text = ""
    if "application/pdf" in content_type or file_url.lower().endswith(".pdf"):
        extracted_text = await extract_text_from_pdf(file_content)
    elif "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in content_type or file_url.lower().endswith(".docx"):
        extracted_text = await extract_text_from_docx(file_content)
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Only PDF and DOCX are supported."
        )

    return {"extracted_text": extracted_text}

# --- How to Run ---
# Save the above code as main.py
# Open your terminal in the same directory and run:
# uvicorn main:app --reload --host 0.0.0.0 --port 8000


@app.get("/hello")
async def Hello():
    
    return {
        "Hello World"
    }

handler = Mangum(app)  # ⬅️ Important for Vercel
