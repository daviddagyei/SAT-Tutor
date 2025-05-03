"""
Tests for the PDF extraction functionality
"""
import os
import pytest
import tempfile
from unittest.mock import patch, MagicMock

from backend.app.utils.pdf_processing.extractor import extract_text_from_pdf


class TestPDFExtractor:
    """Test suite for PDF extractor module"""
    
    def test_extract_text_nonexistent_file(self):
        """Test that extraction raises FileNotFoundError for nonexistent files"""
        with pytest.raises(FileNotFoundError):
            extract_text_from_pdf("/path/to/nonexistent/file.pdf")
            
    def test_extract_text_from_real_pdf(self):
        """Test extraction of text from a real PDF file"""
        # Path to the sample PDF file
        pdf_path = "/home/iamdankwa/SAT-Tutor-2/backend/tests/utils/unit/pdf_processing/sample_pdfs/sat-practice-test-4.pdf"
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
        
        # Copy the sample file if needed
        if not os.path.exists(pdf_path):
            # You might need to adjust this path to where your PDF file is actually located
            sample_file = "vscode-local:/c%3A/Users/dagye/Downloads/sat-practice-test-4.pdf"
            # Copy logic would go here (we'll skip for this test since we're focusing on the test itself)
            pytest.skip("Sample PDF file not available")
        
        # Only run the test if the file exists
        if os.path.exists(pdf_path):
            result = extract_text_from_pdf(pdf_path)
            
            # Basic validation
            assert isinstance(result, dict)
            assert len(result) > 0  # Should have at least one page
            
            # Verify content (adjust these expectations based on the actual PDF content)
            # Check if common SAT keywords are present in any of the pages
            content_found = False
            keywords = ["SAT", "question", "math", "reading", "calculator"]
            
            for page_num, text in result.items():
                if any(keyword.lower() in text.lower() for keyword in keywords):
                    content_found = True
                    break
                    
            assert content_found, "Expected SAT-related content not found in the extracted text"
            
    @patch('backend.app.utils.pdf_processing.extractor.PyPDF2.PdfReader')
    def test_extract_text_from_pdf(self, mock_pdf_reader):
        """Test extraction of text from PDF with mocked PyPDF2"""
        # Create mock PDF pages with text content
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "MATH TEST - Calculator\nQuestion 1: What is 2+2?\nA) 3\nB) 4\nC) 5\nD) 6"
        
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "Question 2: Solve for x: 2x + 3 = 7\nA) x = 2\nB) x = 4\nC) x = 1\nD) x = 3"
        
        # Setup mock reader instance
        mock_reader_instance = MagicMock()
        mock_reader_instance.pages = [mock_page1, mock_page2]
        mock_pdf_reader.return_value = mock_reader_instance
        
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(suffix='.pdf') as temp_pdf:
            result = extract_text_from_pdf(temp_pdf.name)
            
        # Verify the results
        assert len(result) == 2
        assert "MATH TEST - Calculator" in result[1]
        assert "Question 1" in result[1]
        assert "Question 2" in result[2]
        assert "2x + 3 = 7" in result[2]
        
    @patch('backend.app.utils.pdf_processing.extractor.PyPDF2.PdfReader')
    def test_extract_text_with_empty_pages(self, mock_pdf_reader):
        """Test extraction from PDF with empty pages"""
        # Create mock PDF pages with empty content
        mock_page = MagicMock()
        mock_page.extract_text.return_value = ""
        
        # Setup mock reader
        mock_reader_instance = MagicMock()
        mock_reader_instance.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader_instance
        
        # Mock OCR availability (set to False for this test)
        with patch('backend.app.utils.pdf_processing.extractor.OCR_AVAILABLE', False):
            # Create a temporary file for testing
            with tempfile.NamedTemporaryFile(suffix='.pdf') as temp_pdf:
                result = extract_text_from_pdf(temp_pdf.name)
                
            # Verify the result has empty text for the page
            assert len(result) == 1
            assert result[1] == ""
            
    @patch('backend.app.utils.pdf_processing.extractor.PyPDF2.PdfReader')
    def test_extraction_error_handling(self, mock_pdf_reader):
        """Test error handling during extraction"""
        # Make the reader raise an exception
        mock_pdf_reader.side_effect = Exception("Mock PDF extraction error")
        
        # Test that the exception is propagated
        with pytest.raises(Exception) as exc_info:
            with tempfile.NamedTemporaryFile(suffix='.pdf') as temp_pdf:
                extract_text_from_pdf(temp_pdf.name)
                
        assert "Mock PDF extraction error" in str(exc_info.value)