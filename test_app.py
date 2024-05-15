import unittest
import os
from unittest import TestCase, mock
from unittest.mock import patch, MagicMock
from io import BytesIO
from app import app  # Assuming the Flask app is in a file named app.py

class FlaskAppTestCase(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.headers = {
            'Authorization': 'supersecret'  # Replace with your actual shared secret
        }
        
    @patch('app.client.chat.completions.create')
    def test_no_pdf_file_provided(self, mock_openai):
        data = {
            'first_page': '1',
            'last_page': '1',
            'fill_the_blanks': '5',
            'multiple_options': '5',
            'order_the_words': '5'
        }
        response = self.app.post('/quizz', data=data, headers=self.headers, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'No PDF file provided', response.data)
        
    @patch('app.client.chat.completions.create')
    def test_missing_params(self, mock_openai):
        data = {
            'first_page': '1',
            'last_page': '1',
        }
        response = self.app.post('/quizz', data=data, headers=self.headers, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)

    @patch('app.client.chat.completions.create')
    def test_invalid_file_type(self, mock_openai):
        data = {
            'first_page': '1',
            'last_page': '1',
            'fill_the_blanks': '5',
            'multiple_options': '5',
            'order_the_words': '5',
            'pdf_file': (BytesIO(b"Fake content"), 'fakefile.txt')
        }
        response = self.app.post('/quizz', data=data, headers=self.headers, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'File is not a PDF', response.data)

    @patch('app.client.chat.completions.create')
    def test_unauthorized_access(self, mock_openai):
        data = {
            'first_page': '1',
            'last_page': '1',
            'fill_the_blanks': '5',
            'multiple_options': '5',
            'order_the_words': '5',
            'pdf_file': (BytesIO(b"%PDF-1.4"), 'test.pdf')
        }
        response = self.app.post('/quizz', data=data, headers={'Authorization': 'wrongsecret'}, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 401)
        self.assertIn(b'Unauthorized', response.data)
    
    @patch('app.client.chat.completions.create')
    def test_first_page_greater_than_last_page(self, mock_openai):
        data = {
            'first_page': '2',
            'last_page': '1',
            'fill_the_blanks': '5',
            'multiple_options': '5',
            'order_the_words': '5',
            'pdf_file': (BytesIO(b"%PDF-1.4"), 'test.pdf')
        }
        response = self.app.post('/quizz', data=data, headers=self.headers, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'First page cannot be greater than last_page', response.data)

    @patch('app.client.chat.completions.create')
    def test_page_range_exceeds_limit(self, mock_openai):
        data = {
            'first_page': '1',
            'last_page': '12',
            'fill_the_blanks': '5',
            'multiple_options': '5',
            'order_the_words': '5',
            'pdf_file': (BytesIO(b"%PDF-1.4"), 'test.pdf')
        }
        response = self.app.post('/quizz', data=data, headers=self.headers, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Page range exceeds the maximum allowed of 10 pages', response.data)

    @patch('app.client.chat.completions.create')
    def test_error_when_no_questions_sent(self, mock_openai):
        data = {
            'first_page': '1',
            'last_page': '5',
            'fill_the_blanks': '0',
            'multiple_options': '0',
            'order_the_words': '0',
            'pdf_file': (BytesIO(b"%PDF-1.4"), 'test.pdf')
        }
        response = self.app.post('/quizz', data=data, headers=self.headers, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'There should be at least one question', response.data)

    @patch('app.client.chat.completions.create')
    def test_no_error_when_at_least_one_question_sent(self, mock_openai):
        data = {
            'first_page': '1',
            'last_page': '5',
            'fill_the_blanks': '1',
            'multiple_options': '0',
            'order_the_words': '0',
            'pdf_file': (BytesIO(b"%PDF-1.4"), 'test.pdf')
        }
        response = self.app.post('/quizz', data=data, headers=self.headers, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 500) #server error not validation error, thats good


if __name__ == '__main__':
    unittest.main()
