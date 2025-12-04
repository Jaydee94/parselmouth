import google.generativeai as genai
from pathlib import Path
import pypdf
import time
import re
from datetime import datetime
from google.api_core import exceptions


def read_pdf_content(file_path: Path) -> str:
    try:
        reader = pypdf.PdfReader(file_path)
        content = ""
        for page in reader.pages:
            content += page.extract_text() + "\n"
        return content
    except Exception as e:
        raise ValueError(f"Failed to read PDF file: {e}")


def read_text_content(file_path: Path) -> str:
    try:
        return file_path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        raise ValueError("File is not a valid text file or PDF.")


def read_document_content(file_path: Path) -> str:
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if file_path.suffix.lower() == '.pdf':
        return read_pdf_content(file_path)
    else:
        return read_text_content(file_path)


def build_prompt(content: str, include_date: bool, date_format: str, separator: str) -> str:
    prompt_parts = [
        "Analyze the following document content and provide a meaningful, concise title for it.",
        f"The title MUST be in lowercase using '{separator}' as a separator."
    ]
    
    if include_date:
        prompt_parts.append(
            f"If the document contains a specific relevant date (like an invoice date, meeting date, etc.), "
            f"include it at the END of the title in {date_format} format. "
            f"If no date is found, end the title with 'NODATE' as a marker."
        )
    
    prompt_parts.append("Return ONLY the title, nothing else.\n\n")
    prompt_parts.append(f"{content[:10000]}")
    
    return " ".join(prompt_parts)


def normalize_title(title: str, separator: str) -> str:
    title = title.lower()
    if separator and separator != " ":
        title = title.replace(" ", separator).replace("_", separator)
    return title


def add_timestamp_if_needed(title: str, include_date: bool, separator: str) -> str:
    if include_date and title.endswith("nodate"):
        title = title.replace("nodate", "", 1).rstrip(separator)
        current_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        title = f"{title}{separator}{current_timestamp}" if title else current_timestamp
    return title


def generate_title_with_retry(model: genai.GenerativeModel, prompt: str, max_retries: int = 5, base_delay: int = 2) -> str:
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text.strip()
        except exceptions.ResourceExhausted as e:
            if attempt == max_retries - 1:
                raise e
            wait_time = base_delay * (2 ** attempt)
            time.sleep(wait_time)
        except Exception as e:
            raise e
    return ""


def analyze_document(
    file_path: Path, 
    api_key: str, 
    model_name: str = "gemini-2.5-flash",
    include_date: bool = True,
    date_format: str = "YYYY-MM-DD",
    separator: str = "_"
) -> str:
    content = read_document_content(file_path)
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    
    prompt = build_prompt(content, include_date, date_format, separator)
    title = generate_title_with_retry(model, prompt)
    title = normalize_title(title, separator)
    title = add_timestamp_if_needed(title, include_date, separator)
    
    return title
