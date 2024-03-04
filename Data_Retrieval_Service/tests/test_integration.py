import unittest
import requests

class TestMicroserviceIntegration(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://a1eb5b7a783d24cf8b600a46e48d045c-360940722.us-east-2.elb.amazonaws.com:8080"

    def test_url_check(self): 
        response = requests.get(f"{self.base_url}/")
        self.assertEqual(response.status_code, 200)

    def test_user_performance_endpoint(self):
        response = requests.get(f"{self.base_url}/user/performance?contributor=Prasadkpd")
        self.assertEqual(response.status_code, 200)

    def test_contributors_endpoint(self):
        response = requests.get(f"{self.base_url}/contributors?organization=ideaBoostOrg&repo=checkersy-landing")
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()