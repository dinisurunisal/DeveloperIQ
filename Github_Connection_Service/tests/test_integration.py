import unittest
import requests

class TestMicroserviceIntegration(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://ae6ba10e3445d457c92f1d1b3d74df90-1064861151.us-east-2.elb.amazonaws.com:8000"

    def test_url_check(self): 
        response = requests.get(f"{self.base_url}/")
        self.assertEqual(response.status_code, 200)

    def test_token_endpoint(self):
        response = requests.get(f"{self.base_url}/api/github/token")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()