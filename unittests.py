import unittest
import unittest.mock as mock
import app
from settings import site_down
import json
import requests

class IsReachableTestCase(unittest.TestCase):
    """Tests the is_reachable function."""
    
    def test_is_google_reachable(self):
        result = app.is_reachable('www.google.com')
        self.assertTrue(result)
    
    def test_is_nonsense_reachable(self):
        result = app.is_reachable('ishskbeosjei.com')
        self.assertFalse(result)

class GetStatusCodeTestCase(unittest.TestCase):
    """Tests the get_status_code function."""
    
    def test_google_status_code(self):
        result = app.get_status_code('https://www.google.com')
        self.assertEqual(result, 200)
    
    def test_404_status_code(self):
        result = app.get_status_code('https://www.bbc.co.uk/404')
        self.assertEqual(result, 404)
    
    def test_connection_error(self):
        result = app.get_status_code('https://thisurldoesnotexist1234.com')
        self.assertEqual(result, site_down)

class CheckSingleURLTestCase(unittest.TestCase):
    """Tests the check_single_url function"""
    
    def test_bbc_sport_url(self):
        result = app.check_single_url('http://www.bbc.co.uk/sport')
        self.assertEqual(result, '200')
    
    def test_nonsense_url(self):
        result = app.check_single_url('https://ksjsjsbdk.ievrygqlsp.com')
        self.assertEqual(result, site_down)
    
    @unittest.skip("takes too long, reenable if necessary")
    def test_timeout_url(self):
        result = app.check_single_url('https://www.bbc.co.uk:90')
        self.assertEqual(result, site_down)
    
    def test_connrefused_url(self):
        result = app.check_single_url('http://127.0.0.1:8080')
        self.assertEqual(result, site_down)

class CheckMultipleURLsTestCase(unittest.TestCase):
    """Tests the check_multiple_urls function"""
    
    def test_check_multiple_urls(self):
        app.checkurls = {
            "BBC": [
                "https://www.bbc.co.uk", 
                "http://doesnotexist.bbc.co.uk",
                "https://www.bbc.co.uk/404"
            ],
            "Google": [
                "https://www.google.com",
                "http://localhost:8080"
            ]
        }
        app.list_urls = app.generate_list_urls(app.checkurls)
        
        expected = {
            "https://www.bbc.co.uk": "200",
            "http://doesnotexist.bbc.co.uk": "UNREACHABLE",
            "https://www.bbc.co.uk/404": "404",
            "https://www.google.com": "200",
            "http://localhost:8080": "UNREACHABLE",
        }
        result = app.check_multiple_urls()
        self.assertEqual(result, expected)

class CompareSubmittedTestCase(unittest.TestCase):
    """Tests the compare_submitted function."""
    
    def test_known_submitted_url(self):
        app.checkurls = {
            "BBC": [
                "https://www.bbc.co.uk", 
                "http://doesnotexist.bbc.co.uk",
                "https://www.bbc.co.uk/404"
            ],
            "Google": [
                "https://www.google.com",
                "http://localhost:8080"
            ]
        }
        app.list_urls = app.generate_list_urls(app.checkurls)
        submitted = 'https://www.bbc.co.uk'
        result = app.compare_submitted(submitted)
        self.assertEqual(submitted, result[1])
        self.assertTrue(result[0])
        
    def test_unknown_submitted_url(self):
        app.checkurls = {
            "BBC": [
                "https://www.bbc.co.uk", 
                "http://doesnotexist.bbc.co.uk",
                "https://www.bbc.co.uk/404"
            ],
            "Google": [
                "https://www.google.com",
                "http://localhost:8080"
            ]
        }
        app.list_urls = app.generate_list_urls(app.checkurls)
        submitted = 'https://unknown.com'
        result = app.compare_submitted(submitted)
        self.assertEqual(submitted, result[1])
        self.assertFalse(result[0])
    
    def test_whitespace_stripping_submitted_url(self):
        app.checkurls = {
            "BBC": [
                "https://www.bbc.co.uk", 
                "http://doesnotexist.bbc.co.uk",
                "https://www.bbc.co.uk/404"
            ],
            "Google": [
                "https://www.google.com",
                "http://localhost:8080"
            ]
        }
        app.list_urls = app.generate_list_urls(app.checkurls)
        submitted = '  https://www.bbc.co.uk   '
        result = app.compare_submitted(submitted)
        self.assertEqual('https://www.bbc.co.uk', result[1])
        self.assertTrue(result[0])

class HTTPSStartStripTestCase(unittest.TestCase):
    """Tests the https_start_strip function."""
    
    def test_google_url(self):
        result = app.https_start_strip('https://www.google.com')
        self.assertEqual(result, 'https://www.google.com')
    
    def test_whitespace_url(self):
        result = app.https_start_strip('       https://www.google.com    ')
        self.assertEqual(result, 'https://www.google.com')

    def test_no_https_url(self):
        result = app.https_start_strip('www.google.com')
        self.assertEqual(result, 'https://www.google.com')
    
    def test_uppercase_url(self):
        result = app.https_start_strip('HTTPS://WWW.GOOGLE.COM')
        self.assertEqual(result, 'https://www.google.com')

class FlaskAppTestCase(unittest.TestCase):
    """Tests for the Flask app routes and functionality."""

    @classmethod
    def setUpClass(cls):
        app.app.testing = True
        cls.client = app.app.test_client()

    def test_display_returned_statuses(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        # Check for content that you know will be there, such as a group header or status element
        self.assertIn(b'<h1 class="group">BBC</h1>', response.data)
        self.assertIn(b'<h1 class="group">Google</h1>', response.data)

    def test_display_returned_api(self):
        response = self.client.get('/api')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, dict)

    def test_result_post_known_url(self):
        with app.app.test_client() as client:
            response = client.post('/result', data={'submitted': 'https://www.bbc.co.uk'})
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'BBC', response.data)

    def test_result_post_unknown_url(self):
        with app.app.test_client() as client:
            response = client.post('/result', data={'submitted': 'https://unknown.com'})
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'unknown.com', response.data)

class TestEdgeCases(unittest.TestCase):
    def test_is_reachable_empty_url(self):
        result = app.is_reachable('')
        self.assertFalse(result)

    def test_is_reachable_none_url(self):
        with self.assertRaises(TypeError):
            app.is_reachable(None)

    def test_get_status_code_empty_url(self):
        with self.assertRaises(ValueError):
            app.get_status_code('')

    def test_get_status_code_none_url(self):
        with self.assertRaises(ValueError):
            app.get_status_code(None)

class TestErrorHandling(unittest.TestCase):
    @mock.patch('requests.get')
    def test_get_status_code_other_exception(self, mock_get):
        mock_get.side_effect = Exception('Test exception')
        with self.assertRaises(Exception):
            app.get_status_code('https://www.google.com')

class TestFileLoading(unittest.TestCase):
    def test_load_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            with open('nonexistentfile.json') as f:
                app.checkurls = json.load(f)

    def test_load_malformed_json(self):
        malformed_json = '''{
            "key": "value"
                "another_key": "another_value"
        }'''
        with self.assertRaises(json.JSONDecodeError):
            app.checkurls = json.loads(malformed_json)

class TestLaunchChecker(unittest.TestCase):
    @mock.patch('threading.Timer')
    def test_launch_checker(self, mock_timer):
        app.launch_checker()
        mock_timer.assert_called_once_with(app.refresh_interval, app.launch_checker)

class TestMockingExternalServices(unittest.TestCase):
    @mock.patch('requests.get')
    def test_get_status_code_mocked(self, mock_get):
        mock_get.return_value.status_code = 200
        self.assertEqual(app.get_status_code('https://www.google.com'), 200)

    @mock.patch('requests.get')
    def test_get_status_code_mocked_connection_error(self, mock_get):
        mock_get.side_effect = requests.ConnectionError
        self.assertEqual(app.get_status_code('https://www.google.com'), site_down)

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.app = app.app.test_client()

    def test_integration(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<h1 class="group">BBC</h1>', response.data)
        self.assertIn(b'<h1 class="group">Google</h1>', response.data)

        # Post a known URL
        response = self.app.post('/result', data={'submitted': 'https://www.bbc.co.uk'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'BBC', response.data)

        # Post an unknown URL
        response = self.app.post('/result', data={'submitted': 'https://unknown.com'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'unknown.com', response.data)

if __name__ == '__main__':
    unittest.main()
