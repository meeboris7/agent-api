import os
import json
import requests
from io import BytesIO
from pypdf import PdfReader
from docx import Document

def handler(request, response):
    if request.method != 'POST':
        response.status_code = 405 
        return {'status': 'error', 'message': 'Only POST requests are allowed'}

    try:
        data = request.json()
        file_url = data.get('file_url')

        if not file_url:
            response.status_code = 400 
            return {'status': 'error', 'message': '`file_url` is required in the request body'}


        try:
            r = requests.get(file_url, stream=True, timeout=10) 
            r.raise_for_status() 
            file_bytes = BytesIO(r.content) 
        except requests.exceptions.RequestException as e:
            response.status_code = 400
            return {'status': 'error', 'message': f"Failed to download file from URL: {e}"}

        text = ""

        if file_url.lower().endswith('.pdf'):
            try:
                reader = PdfReader(file_bytes)
                for page in reader.pages:
                    text += page.extract_text() or ""
            except Exception as e:
                response.status_code = 500
                return {'status': 'error', 'message': f"Error parsing PDF: {e}"}
        elif file_url.lower().endswith('.docx'):
            try:
                doc = Document(file_bytes)
                for para in doc.paragraphs:
                    text += para.text + "\n"
            except Exception as e:
                response.status_code = 500
                return {'status': 'error', 'message': f"Error parsing DOCX: {e}"}
        else:
            response.status_code = 400
            return {'status': 'error', 'message': "Unsupported file type. Only PDF and DOCX are supported."}

        
        response.status_code = 200 
        return {
            'status': 'success',
            'document_text': text
        }

    except json.JSONDecodeError:
        response.status_code = 400
        return {'status': 'error', 'message': 'Invalid JSON in request body'}
    except Exception as e:
        response.status_code = 500
        return {'status': 'error', 'message': f"An unexpected error occurred: {e}"}