import unittest
import requests

class TestMicroserviceIntegration(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://a2b81ea6b1ca647949ff43098c1d7170-1678422433.us-east-2.elb.amazonaws.com:5000"

    def test_url_check(self): 
        response = requests.get(f"{self.base_url}/")
        self.assertEqual(response.status_code, 200)

    def test_get_contributions_endpoint(self):
        response = requests.get(f"{self.base_url}/api/dynamodb/get_item?contributor=Prasadkpd")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()