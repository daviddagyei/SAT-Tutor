"""
Tests for the PDF processing CLI module
"""
import sys
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from backend.app.utils.pdf_processing.cli import main


class TestCLI:
    """Test suite for the PDF processing command-line interface"""
    
    @patch('backend.app.utils.pdf_processing.cli.process_pdf_to_questions')
    @patch('backend.app.utils.pdf_processing.cli.argparse.ArgumentParser.parse_args')
    def test_cli_single_pdf_json_only(self, mock_parse_args, mock_process_pdf):
        """Test CLI with single PDF in JSON-only mode"""
        # Mock arguments
        mock_args = MagicMock()
        mock_args.pdf_path = '/path/to/test.pdf'
        mock_args.pdf_dir = None
        mock_args.json_only = True
        mock_args.output_dir = None
        mock_parse_args.return_value = mock_args
        
        # Mock PDF processing
        mock_questions = [{"id": "q1", "text": "Question 1"}]
        mock_process_pdf.return_value = mock_questions
        
        # Mock file existence check
        with patch('backend.app.utils.pdf_processing.cli.os.path.exists', return_value=True):
            # Call the main function
            exit_code = main()
            
            # Verify it was called correctly and returned success
            mock_process_pdf.assert_called_once()
            assert exit_code == 0
    
    @patch('backend.app.utils.pdf_processing.cli.process_pdf_and_store_in_db')
    @patch('backend.app.utils.pdf_processing.cli.argparse.ArgumentParser.parse_args')
    def test_cli_single_pdf_with_db_storage(self, mock_parse_args, mock_process_pdf):
        """Test CLI with single PDF with database storage"""
        # Mock arguments
        mock_args = MagicMock()
        mock_args.pdf_path = '/path/to/test.pdf'
        mock_args.pdf_dir = None
        mock_args.json_only = False
        mock_args.output_dir = None
        mock_parse_args.return_value = mock_args
        
        # Mock PDF processing and DB storage
        mock_process_pdf.return_value = (5, 5)  # 5 questions processed, 5 stored
        
        # Mock file existence check
        with patch('backend.app.utils.pdf_processing.cli.os.path.exists', return_value=True):
            # Call the main function
            exit_code = main()
            
            # Verify it was called correctly and returned success
            mock_process_pdf.assert_called_once_with('/path/to/test.pdf')
            assert exit_code == 0
    
    @patch('backend.app.utils.pdf_processing.cli.batch_process_pdfs')
    @patch('backend.app.utils.pdf_processing.cli.argparse.ArgumentParser.parse_args')
    def test_cli_batch_processing(self, mock_parse_args, mock_batch_process):
        """Test CLI with batch PDF processing"""
        # Mock arguments
        mock_args = MagicMock()
        mock_args.pdf_path = None
        mock_args.pdf_dir = '/path/to/pdf_folder'
        mock_args.json_only = False
        mock_args.output_dir = '/path/to/output'
        mock_parse_args.return_value = mock_args
        
        # Mock batch processing
        mock_batch_process.return_value = {
            'test1.pdf': (3, 3),
            'test2.pdf': (2, 2)
        }
        
        # Mock directory existence check
        with patch('backend.app.utils.pdf_processing.cli.os.path.exists', return_value=True):
            # Call the main function
            exit_code = main()
            
            # Verify it was called correctly and returned success
            mock_batch_process.assert_called_once_with('/path/to/pdf_folder', '/path/to/output')
            assert exit_code == 0
    
    @patch('backend.app.utils.pdf_processing.cli.process_pdf_to_questions')
    @patch('backend.app.utils.pdf_processing.cli.argparse.ArgumentParser.parse_args')
    def test_cli_nonexistent_pdf(self, mock_parse_args, mock_process_pdf):
        """Test CLI with nonexistent PDF file"""
        # Mock arguments
        mock_args = MagicMock()
        mock_args.pdf_path = '/path/to/nonexistent.pdf'
        mock_args.pdf_dir = None
        mock_args.json_only = True
        mock_parse_args.return_value = mock_args
        
        # Mock file existence check
        with patch('backend.app.utils.pdf_processing.cli.os.path.exists', return_value=False):
            # Call the main function
            exit_code = main()
            
            # Verify it returned error code
            assert exit_code == 1
            mock_process_pdf.assert_not_called()
    
    @patch('backend.app.utils.pdf_processing.cli.argparse.ArgumentParser.parse_args')
    def test_cli_error_handling(self, mock_parse_args):
        """Test CLI error handling"""
        # Mock arguments
        mock_args = MagicMock()
        mock_args.pdf_path = '/path/to/test.pdf'
        mock_args.pdf_dir = None
        mock_args.json_only = True
        mock_parse_args.return_value = mock_args
        
        # Mock file existence check
        with patch('backend.app.utils.pdf_processing.cli.os.path.exists', return_value=True):
            # Mock process_pdf_to_questions to throw an exception
            with patch('backend.app.utils.pdf_processing.cli.process_pdf_to_questions',
                      side_effect=Exception("Processing error")):
                # Call the main function
                exit_code = main()
                
                # Verify it returned error code
                assert exit_code == 1