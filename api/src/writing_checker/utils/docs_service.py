from PyPDF2 import PdfReader
from docx import Document
import re


def get_pdf_text(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


def docx_to_text(docx_path: str):
    doc = Document(docx_path)
    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)
    return '\n'.join(full_text)


def count_words(essay):
    # Words to exclude
    exclude_words = {'an', 'of', 'the', 'a', 'in'}

    # Step 2: Clean the text
    cleaned_essay = re.sub(r'[^\w\s]', '', essay)  # Remove punctuation
    cleaned_essay = cleaned_essay.strip()  # Remove leading/trailing whitespace

    # Step 3: Split the text into words
    words = cleaned_essay.split()

    # Step 4: Filter out the excluded words and count the remaining words
    filtered_words = [word for word in words if word.lower() not in exclude_words]
    word_count = len(filtered_words)

    return word_count

