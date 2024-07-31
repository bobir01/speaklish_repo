import unittest
from django.test import Client
from rest_framework import status


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client()

    def test_part1_question_list(self):
        response = self.client.get('/api/part1/questions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_part1_question_retrieve_update_destroy(self):
        response = self.client.get('/api/part1/questions/1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.put('/api/part1/questions/1/', {'question_txt': 'Updated question'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.delete('/api/part1/questions/1/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_part1_question_create(self):
        response = self.client.post('/api/part1/questions/', {'question_txt': 'New question'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Add more tests for other API views...


if __name__ == '__main__':
    unittest.main()
