"""
LibraryHTTPClient 테스트 코드
"""

import unittest
from unittest.mock import patch, MagicMock, Mock
import json
import requests
from requests.exceptions import RequestException

from kgu_library.library.http_client import LibraryHTTPClient
from kgu_library.library.exceptions import APIResponseError


class TestLibraryHTTPClient(unittest.TestCase):
    """LibraryHTTPClient 테스트 클래스"""

    def setUp(self):
        """테스트 설정"""
        self.client = LibraryHTTPClient()
        self.test_endpoint = "test/endpoint"
        self.test_url = f"{self.client.BASE_URL}/{self.test_endpoint}"
        self.test_params = {"param1": "value1", "param2": "value2"}
        self.test_headers = {"X-Custom-Header": "test-value"}
        self.test_data = {"data1": "value1", "data2": "value2"}
        self.test_json_data = {"json_key1": "value1", "json_key2": "value2"}

    def test_init(self):
        """초기화 테스트"""
        # 세션 헤더 확인
        self.assertIn("User-Agent", self.client.session.headers)
        self.assertIn("Accept", self.client.session.headers)
        self.assertIn("Origin", self.client.session.headers)

        # SSL 검증 비활성화 확인
        self.assertFalse(self.client.session.verify)

    @patch("requests.Session.get")
    def test_get_success(self, mock_get):
        """GET 요청 성공 테스트"""
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "data": {"key": "value"}}
        mock_get.return_value = mock_response

        # GET 요청 호출
        result = self.client.get(
            self.test_endpoint, params=self.test_params, headers=self.test_headers
        )

        # 결과 검증
        self.assertEqual(result, {"success": True, "data": {"key": "value"}})

        # 올바른 인자로 요청되었는지 확인
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], self.test_url)
        self.assertEqual(kwargs["params"], self.test_params)

        # 헤더 병합 검증
        headers = kwargs["headers"]
        self.assertIn("Host", headers)
        self.assertIn("Accept", headers)
        self.assertIn("Referer", headers)
        self.assertEqual(headers["X-Custom-Header"], "test-value")

    @patch("requests.Session.get")
    def test_get_json_decode_error(self, mock_get):
        """GET 요청 JSON 디코딩 오류 테스트"""
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_get.return_value = mock_response

        # 예외 발생 검증
        with self.assertRaises(APIResponseError):
            self.client.get(self.test_endpoint)

    @patch("requests.Session.get")
    def test_get_http_error(self, mock_get):
        """GET 요청 HTTP 오류 테스트"""
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # 예외 발생 검증
        with self.assertRaises(APIResponseError):
            self.client.get(self.test_endpoint)

    @patch("requests.Session.get")
    def test_get_request_exception(self, mock_get):
        """GET 요청 네트워크 오류 테스트"""
        # Mock 예외 설정
        mock_get.side_effect = RequestException("Connection error")

        # 예외 발생 검증
        with self.assertRaises(APIResponseError):
            self.client.get(self.test_endpoint)

    @patch("requests.Session.post")
    def test_post_with_json_data_success(self, mock_post):
        """JSON 데이터로 POST 요청 성공 테스트"""
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "data": "result"}
        mock_post.return_value = mock_response

        # POST 요청 호출
        result = self.client.post(
            self.test_endpoint, json_data=self.test_json_data, headers=self.test_headers
        )

        # 결과 검증
        self.assertEqual(result, {"success": True, "data": "result"})

        # 올바른 인자로 요청되었는지 확인
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], self.test_url)
        self.assertEqual(kwargs["json"], self.test_json_data)

        # 헤더 병합 및 Content-Type 확인
        headers = kwargs["headers"]
        self.assertEqual(headers["Content-Type"], "application/json")
        self.assertEqual(headers["X-Custom-Header"], "test-value")

    @patch("requests.Session.post")
    def test_post_with_form_data_success(self, mock_post):
        """폼 데이터로 POST 요청 성공 테스트"""
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "data": "result"}
        mock_post.return_value = mock_response

        # POST 요청 호출
        result = self.client.post(
            self.test_endpoint, data=self.test_data, headers=self.test_headers
        )

        # 결과 검증
        self.assertEqual(result, {"success": True, "data": "result"})

        # 올바른 인자로 요청되었는지 확인
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], self.test_url)
        self.assertEqual(kwargs["data"], self.test_data)

        # Content-Type이 설정되지 않았는지 확인 (폼 데이터이므로)
        headers = kwargs["headers"]
        self.assertNotIn("Content-Type", headers)

    @patch("requests.Session.post")
    def test_post_json_decode_error_empty_response(self, mock_post):
        """POST 요청 JSON 디코딩 오류 (빈 응답) 테스트"""
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_post.return_value = mock_response

        # 요청 실행 (오류 없이 성공해야 함)
        result = self.client.post(self.test_endpoint)

        # 빈 성공 객체 반환 확인
        self.assertEqual(result, {"success": True})

    @patch("requests.Session.post")
    def test_post_http_error(self, mock_post):
        """POST 요청 HTTP 오류 테스트"""
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        # 예외 발생 검증
        with self.assertRaises(APIResponseError):
            self.client.post(self.test_endpoint)

    @patch("requests.Session.post")
    def test_post_request_exception(self, mock_post):
        """POST 요청 네트워크 오류 테스트"""
        # Mock 예외 설정
        mock_post.side_effect = RequestException("Connection error")

        # 예외 발생 검증
        with self.assertRaises(APIResponseError):
            self.client.post(self.test_endpoint)


if __name__ == "__main__":
    unittest.main()
