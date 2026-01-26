import concurrent.futures
import os
import re
import nltk
from nltk.corpus import stopwords
import filetype
import PyPDF2
from tabula import read_pdf
from docx import Document
import pandas as pd
from bs4 import BeautifulSoup


nltk.download('stopwords')


def parse_pdf(file_path):
    text = ""
    try:
        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            num_pages = len(pdf_reader.pages)
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
        # 处理可能存在的表格
        tables = read_pdf(file_path, pages='all')
        for table in tables:
            text += str(table)
    except Exception as e:
        print(f"Error parsing PDF: {e}")
    return text


def parse_docx(file_path):
    doc = Document(file_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text


def parse_excel(file_path):
    try:
        df = pd.read_excel(file_path)
        text = ""
        for index, row in df.iterrows():
            for value in row:
                text += str(value) + " "
            text += "\n"
    except Exception as e:
        print(f"Error parsing Excel: {e}")
    return text


def parse_html(file_path):
    with open(file_path, 'r', encoding='utf - 8') as html_file:
        soup = BeautifulSoup(html_file, 'html.parser')
        text = soup.get_text()
    return text


def parse_txt(file_path):
    with open(file_path, 'r', encoding='utf - 8') as txt_file:
        text = txt_file.read()
    return text


def clean_text(text):
    text = re.sub('<.*?>', '', text)  # 去除HTML标签
    text = re.sub('[^a-zA-Z0 - 9\s.,?!]', '', text)  # 去除特殊字符
    return text


def remove_stopwords(text):
    stop_words = set(stopwords.words('english'))
    words = text.split()
    filtered_words = [word for word in words if word.lower() not in stop_words]
    return " ".join(filtered_words)


def standardize_text(text):
    return text.lower()


def process_file(file_path):
    kind = filetype.guess(file_path)
    if kind is None:
        print(f"无法识别文件格式: {file_path}")
        return ""
    file_extension = kind.extension
    if file_extension == 'pdf':
        text = parse_pdf(file_path)
    elif file_extension == 'docx':
        text = parse_docx(file_path)
    elif file_extension == 'xlsx':
        text = parse_excel(file_path)
    elif file_extension == 'html':
        text = parse_html(file_path)
    elif file_extension == 'txt':
        text = parse_txt(file_path)
    else:
        print(f"不支持的文件格式: {file_path}")
        return ""
    text = clean_text(text)
    text = remove_stopwords(text)
    text = standardize_text(text)
    return text


def process_files_in_directory(directory):
    all_texts = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        file_paths = [os.path.join(directory, file) for file in os.listdir(directory) if
                      os.path.isfile(os.path.join(directory, file))]
        future_to_file = {executor.submit(process_file, file_path): file_path for file_path in file_paths}
        for future in concurrent.futures.as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                text = future.result()
                all_texts.append(text)
            except Exception as e:
                print(f"处理文件 {file_path} 时出错: {e}")
    return all_texts


if __name__ == "__main__":
    directory = "your_directory_path"
    texts = process_files_in_directory(directory)
    print(texts)