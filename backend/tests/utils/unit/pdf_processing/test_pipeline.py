"""
Tests for the main PDF processing pipeline
"""
import os
import json
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from backend.app.utils.pdf_processing.pipeline import (
    process_pdf_to_questions,
    process_pdf_and_store_in_db,
    batch_process_pdfs
)


class TestPipeline:
    """Test suite for the main pipeline module"""
    
    @patch('backend.app.utils.pdf_processing.pipeline.extract_text_from_pdf')
    @patch('backend.app.utils.pdf_processing.pipeline.process_text_to_sections')
    @patch('backend.app.utils.pdf_processing.pipeline.extract_questions_from_section')
    @patch('backend.app.utils.pdf_processing.pipeline.transform_questions_to_json')
    def test_process_pdf_to_questions(self, mock_transform, mock_extract_questions, 
                                     mock_process_sections, mock_extract_text):
        """Test the end-to-end PDF processing pipeline"""
        # Mock the extraction of text from PDF
        mock_extract_text.return_value = {
            1: "Page 1 content",
            2: "Page 2 content"
        }
        
        # Mock the processing of text into sections
        from backend.app.utils.pdf_processing.processor import SATSection
        mock_sections = {
            SATSection.MATH: ["Math section content"],
            SATSection.READING_WRITING: ["Reading section content"]
        }
        mock_process_sections.return_value = mock_sections
        
        # Mock the extraction of questions from sections
        mock_math_questions = [{"text": "Math question 1"}, {"text": "Math question 2"}]
        mock_reading_questions = [{"text": "Reading question"}]
        mock_extract_questions.side_effect = [mock_math_questions, mock_reading_questions]
        
        # Mock the transformation of questions to JSON
        mock_json_questions = [
            {"id": "q1", "text": "Math question 1", "topic_id": "math_topic"},
            {"id": "q2", "text": "Math question 2", "topic_id": "math_topic"},
            {"id": "q3", "text": "Reading question", "topic_id": "reading_topic"}
        ]
        mock_transform.return_value = mock_json_questions
        
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(suffix='.pdf') as temp_pdf:
            # Test with output JSON
            with tempfile.NamedTemporaryFile(suffix='.json') as temp_json:
                result = process_pdf_to_questions(temp_pdf.name, temp_json.name)
                
                # Verify calls to the pipeline components
                mock_extract_text.assert_called_once_with(temp_pdf.name)
                mock_process_sections.assert_called_once_with(mock_extract_text.return_value)
                assert mock_extract_questions.call_count == 2
                
                # Check that the transform was called with all questions
                expected_questions = mock_math_questions + mock_reading_questions
                mock_transform.assert_called_once()
                
                # Verify that JSON was written to the output file
                with open(temp_json.name, 'r') as f:
                    saved_json = json.load(f)
                    assert len(saved_json) == 3
                    assert saved_json == mock_json_questions
                
                # Verify the returned questions
                assert len(result) == 3
                assert result == mock_json_questions
    
    @patch('backend.app.utils.pdf_processing.pipeline.process_pdf_to_questions')
    def test_process_pdf_and_store_in_db(self, mock_process_pdf):
        """Test processing PDF and storing in database"""
        # Mock the PDF processing
        mock_questions = [
            {"id": "q1", "text": "Question 1", "topic_id": "topic1"},
            {"id": "q2", "text": "Question 2", "topic_id": "topic2"}
        ]
        mock_process_pdf.return_value = mock_questions
        
        # Mock the repository
        mock_repo = MagicMock()
        mock_repo.create.return_value = True
        
        # Patch the import inside the function instead of the attribute directly
        with patch('backend.app.repositories.question_repository.QuestionRepository', 
                  return_value=mock_repo):
            # Test with a temporary file
            with tempfile.NamedTemporaryFile(suffix='.pdf') as temp_pdf:
                processed, stored = process_pdf_and_store_in_db(temp_pdf.name, save_json=False)
                
                # Verify process_pdf_to_questions was called
                mock_process_pdf.assert_called_once()
                
                # Verify questions were stored
                assert processed == 2
                assert stored == 2
                
    @patch('backend.app.utils.pdf_processing.pipeline.os.path.exists')
    @patch('backend.app.utils.pdf_processing.pipeline.os.listdir')
    @patch('backend.app.utils.pdf_processing.pipeline.process_pdf_and_store_in_db')
    def test_batch_process_pdfs(self, mock_process_pdf, mock_listdir, mock_exists):
        """Test batch processing of multiple PDFs"""
        # Mock directory existence check
        mock_exists.return_value = True
        
        # Mock directory listing
        mock_listdir.return_value = ['test1.pdf', 'test2.pdf', 'not_a_pdf.txt']
        
        # Mock processing results
        mock_process_pdf.side_effect = [(3, 3), (2, 2)]
        
        # Test batch processing
        results = batch_process_pdfs('/fake/pdf/dir')
        
        # Verify process_pdf_and_store_in_db was called for each PDF
        assert mock_process_pdf.call_count == 2
        
        # Check results
        assert len(results) == 2
        assert results['test1.pdf'] == (3, 3)
        assert results['test2.pdf'] == (2, 2)
        assert 'not_a_pdf.txt' not in results
        
    @patch('backend.app.utils.pdf_processing.pipeline.os.path.exists')
    def test_batch_process_nonexistent_directory(self, mock_exists):
        """Test batch processing with nonexistent directory"""
        # Mock directory existence check
        mock_exists.return_value = False
        
        # Test with nonexistent directory
        with pytest.raises(FileNotFoundError):
            batch_process_pdfs('/nonexistent/directory')

    @patch('backend.app.utils.pdf_processing.pipeline.process_pdf_and_store_in_db')
    @patch('backend.app.utils.pdf_processing.pipeline.os.path.exists')
    @patch('backend.app.utils.pdf_processing.pipeline.os.listdir')
    def test_batch_process_with_errors(self, mock_listdir, mock_exists, mock_process_pdf):
        """Test batch processing with errors in some PDFs"""
        # Mock directory existence check
        mock_exists.return_value = True
        
        # Mock directory listing
        mock_listdir.return_value = ['good.pdf', 'bad.pdf']
        
        # Mock processing - second one raises exception
        mock_process_pdf.side_effect = [(2, 2), Exception("Processing error")]
        
        # Test batch processing with error handling
        results = batch_process_pdfs('/fake/pdf/dir')
        
        # Verify process_pdf_and_store_in_db was called for each PDF
        assert mock_process_pdf.call_count == 2
        
        # Check results - should include the error case with (0, 0)
        assert len(results) == 2
        assert results['good.pdf'] == (2, 2)
        assert results['bad.pdf'] == (0, 0)