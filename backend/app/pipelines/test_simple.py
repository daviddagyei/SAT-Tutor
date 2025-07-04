#!/usr/bin/env python3

import os
import sys
sys.path.append('/home/iamdankwa/SAT-Tutor-2/backend/app')

# Test basic imports
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    print("✓ ChatGoogleGenerativeAI imported successfully")
except ImportError as e:
    print(f"✗ Failed to import ChatGoogleGenerativeAI: {e}")
    sys.exit(1)

try:
    from langgraph.graph import StateGraph, START, END
    print("✓ LangGraph imported successfully")
except ImportError as e:
    print(f"✗ Failed to import LangGraph: {e}")
    sys.exit(1)

try:
    from langchain_community.document_loaders import PyPDFLoader
    print("✓ PyPDFLoader imported successfully")
except ImportError as e:
    print(f"✗ Failed to import PyPDFLoader: {e}")
    sys.exit(1)

# Test loading a PDF
try:
    current_dir = os.path.dirname(__file__)
    questions_pdf = os.path.join(current_dir, "sat-questions.pdf")
    
    if os.path.exists(questions_pdf):
        print(f"✓ Questions PDF found: {questions_pdf}")
        loader = PyPDFLoader(questions_pdf)
        pages = loader.load()
        print(f"✓ Successfully loaded {len(pages)} pages")
        
        # Show first page preview
        if pages:
            first_page = pages[0].page_content[:200]
            print(f"✓ First page preview: {first_page}...")
    else:
        print(f"✗ Questions PDF not found: {questions_pdf}")
        
except Exception as e:
    print(f"✗ Error loading PDF: {e}")

print("\nAll basic checks completed!")
