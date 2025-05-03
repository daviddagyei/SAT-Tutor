"""
Script to create a sample PDF file for testing
"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

def create_sample_pdf(output_path):
    """Create a simple PDF with SAT-like content for testing"""
    c = canvas.Canvas(output_path, pagesize=letter)
    
    # Page 1 - Math Section
    c.setFont("Helvetica", 14)
    c.drawString(50, 750, "SAT Practice Test")
    c.setFont("Helvetica", 12)
    c.drawString(50, 720, "MATH TEST - Calculator")
    c.drawString(50, 680, "Question 1: What is 2+2?")
    c.drawString(70, 660, "A) 3")
    c.drawString(70, 640, "B) 4")
    c.drawString(70, 620, "C) 5")
    c.drawString(70, 600, "D) 6")
    c.drawString(50, 560, "Question 2: Solve for x: 2x + 3 = 7")
    c.drawString(70, 540, "A) x = 2")
    c.drawString(70, 520, "B) x = 4")
    c.drawString(70, 500, "C) x = 1")
    c.drawString(70, 480, "D) x = 3")
    c.showPage()
    
    # Page 2 - Reading Section
    c.setFont("Helvetica", 14)
    c.drawString(50, 750, "SAT Practice Test")
    c.setFont("Helvetica", 12)
    c.drawString(50, 720, "READING TEST")
    c.drawString(50, 680, "This passage is adapted from a novel set in the early 1900s.")
    c.drawString(50, 640, "Lorem ipsum dolor sit amet, consectetur adipiscing elit.")
    c.drawString(50, 620, "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.")
    c.drawString(50, 600, "Ut enim ad minim veniam, quis nostrud exercitation ullamco.")
    c.drawString(50, 560, "Question 3: Based on the passage, the author most likely believes:")
    c.drawString(70, 540, "A) Time is valuable")
    c.drawString(70, 520, "B) Nature is unpredictable")
    c.drawString(70, 500, "C) Knowledge is power")
    c.drawString(70, 480, "D) Change is inevitable")
    c.showPage()
    
    c.save()

if __name__ == "__main__":
    output_dir = "/home/iamdankwa/SAT-Tutor-2/backend/tests/utils/unit/pdf_processing/sample_pdfs"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "sat-practice-test-4.pdf")
    create_sample_pdf(output_path)
    print(f"Sample PDF created at: {output_path}")