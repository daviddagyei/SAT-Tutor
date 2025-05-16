import os
import re
import json
import fitz  # PyMuPDF
from pdf2image import convert_from_path
from PIL import Image
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Configure your OpenAI API key

# === Configuration ===
QUESTION_PDF = 'sat_questions.pdf'
ANSWER_PDF = 'sat_answers.pdf'
OUTPUT_JSON = 'sat_questions.json'
IMAGE_OUTPUT_DIR = 'question_images'
DPI = 150

# Ensure output directory exists
os.makedirs(IMAGE_OUTPUT_DIR, exist_ok=True)

# Utility: generate question ID
def make_question_id(section: str, module: int, qnum: int, part: str = None) -> str:
    sec = 'RW' if section.lower().startswith('read') else 'M'
    mod = f"M{module}"
    qid = f"{sec}-{mod}-Q{qnum:02d}"
    if part:
        qid += part.lower()
    return qid

# 1. Extract text blocks and question boundaries from PDF
def extract_question_texts(pdf_path):
    doc = fitz.open(pdf_path)
    questions = []
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text('text').splitlines()
        # Simple regex: lines starting with digit+
        pattern = re.compile(r'^(\d+)\b')
        current = None
        for line in text:
            m = pattern.match(line)
            if m:
                # start of new question
                if current:
                    questions.append(current)
                qnum = int(m.group(1))
                current = {'page': page_num, 'qnum': qnum, 'lines': [line]}
            elif current:
                current['lines'].append(line)
        if current:
            questions.append(current)
    return questions

# 2. Crop question region and save image
def save_question_images(pdf_path, questions):
    doc = fitz.open(pdf_path)
    for q in questions:
        page = doc[q['page'] - 1]
        # crude: capture full page for now
        pix = page.get_pixmap(dpi=DPI)
        img_path = os.path.join(IMAGE_OUTPUT_DIR, f"Q{q['qnum']:02d}.png")
        pix.save(img_path)
        q['image'] = img_path

# 3. Call GPT to convert question to JSON schema
def call_gpt(question_text, question_id):
    prompt = (
        "You are a tool that converts an SAT question into a JSON object with the keys:\n"
        "id, section, module, question_number, type, category, stimulus, choices, correct.\n"
        "Respond with only valid JSON, no extra explanation.\n"
        f"Question ID: {question_id}\n"
        f"Question:\n{question_text}\n"
    )
    resp = client.chat.completions.create(model='gpt-4',
    messages=[{'role':'system','content':prompt}],
    temperature=0)
    content = resp.choices[0].message.content
    return json.loads(content)

# 4. Parse answer key PDF
def extract_answers(answer_pdf):
    # Simplest: OCR or text extract list of number + letter
    doc = fitz.open(answer_pdf)
    answers = {}
    current_section = None
    for page in doc:
        text = page.get_text('text').splitlines()
        for line in text:
            # detect section headers
            if 'reading' in line.lower():
                current_section = 'Reading and Writing'
            elif 'math' in line.lower():
                current_section = 'Math'
            m = re.match(r"(\d+)\.\s*([A-D])", line)
            if m and current_section:
                qnum = int(m.group(1))
                ans = m.group(2)
                # assume module ordering or default module=1
                qid = make_question_id(current_section, 1, qnum)
                answers[qid] = ans
    return answers

# 5. Assemble pipeline
def main():
    questions = extract_question_texts(QUESTION_PDF)
    save_question_images(QUESTION_PDF, questions)

    json_list = []
    for q in questions:
        text = '\n'.join(q['lines'])
        qid = make_question_id('Reading and Writing', 1, q['qnum'])
        q_json = call_gpt(text, qid)
        q_json['image'] = q['image']
        json_list.append(q_json)

    answers = extract_answers(ANSWER_PDF)
    for obj in json_list:
        if obj['id'] in answers:
            obj['correct'] = answers[obj['id']]

    with open(OUTPUT_JSON, 'w') as f:
        json.dump(json_list, f, indent=2)
    print(f"Wrote output to {OUTPUT_JSON}")

if __name__ == '__main__':
    main()
