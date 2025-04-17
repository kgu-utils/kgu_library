"""
LibraryAPIWrapper 테스트 코드
"""

import unittest
from unittest.mock import patch, MagicMock
import json
from typing import Dict, Any, Tuple

from kgu_library.library.api import LibraryAPIWrapper
from kgu_library.library.enums import BookingStatus
from kgu_library.library.exceptions import LoginError, BookingError, APIResponseError


class TestLibraryAPIWrapper(unittest.TestCase):
    """LibraryAPIWrapper 테스트 클래스"""

    def setUp(self):
        """테스트 설정"""
        self.api = LibraryAPIWrapper()
        self.test_user_id = "202400000"
        self.test_name = "테스트"

    @patch("requests.Session.post")
    def test_login_success(self, mock_post):
        """로그인 성공 테스트"""
        # Mock 응답 설정
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}

        # 세션 쿠키 설정
        mock_cookie = MagicMock()
        mock_cookie.name = "CLI_ID"
        mock_post.return_value = mock_response
        mock_post.return_value.cookies = [mock_cookie]

        # 로그인 요청
        result = self.api.login(self.test_user_id, self.test_name)

        # 결과 검증
        self.assertTrue(result)

        # POST 요청이 올바른 인자로 호출되었는지 확인
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertIn("/login_library", args[0])
        self.assertIn("data", kwargs)
        self.assertIn("headers", kwargs)

        # 데이터에 학번과 이름 확인
        data = kwargs.get("data", "")
        self.assertIn(self.test_user_id, data)
        self.assertIn(self.test_name, data)

    @patch("requests.Session.post")
    def test_login_failure(self, mock_post):
        """로그인 실패 테스트"""
        # Mock 응답 설정
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": False}
        mock_response.cookies = []

        # 응답 설정
        mock_post.return_value = mock_response

        # 로그인 요청
        result = self.api.login(self.test_user_id, self.test_name)

        # 결과 검증
        self.assertFalse(result)

    @patch("kgu_library.library.http_client.LibraryHTTPClient.get")
    def test_check_my_status_with_seat(self, mock_get):
        """좌석 예약 상태 조회 (좌석 있음) 테스트"""
        # Mock 응답 데이터
        mock_response = {
            "success": True,
            "data": {
                "mySeat": {"seatId": 123, "areaName": "도서관 1층", "seatName": "A-123"}
            },
        }

        # Mock 설정
        mock_get.return_value = mock_response

        # 상태 조회 요청
        result = self.api.check_my_status()

        # 결과 검증
        self.assertIsNotNone(result)
        self.assertEqual(result["seatId"], 123)
        self.assertEqual(result["areaName"], "도서관 1층")
        self.assertEqual(result["seatName"], "A-123")

        # 올바른 엔드포인트로 요청되었는지 확인
        mock_get.assert_called_with("user/my-status")

    @patch("kgu_library.library.http_client.LibraryHTTPClient.get")
    def test_check_my_status_no_seat(self, mock_get):
        """좌석 예약 상태 조회 (좌석 없음) 테스트"""
        # Mock 응답 데이터 (좌석 정보 없음)
        mock_response = {"success": True, "data": {"mySeat": None}}

        # Mock 설정
        mock_get.return_value = mock_response

        # 상태 조회 요청
        result = self.api.check_my_status()

        # 결과 검증
        self.assertIsNone(result)

        # 올바른 엔드포인트로 요청되었는지 확인
        mock_get.assert_called_with("user/my-status")

    @patch("kgu_library.library.http_client.LibraryHTTPClient.post")
    def test_book_seat_success(self, mock_post):
        """좌석 예약 성공 테스트"""
        # Mock 응답 데이터
        mock_response = {"success": True, "code": 1, "status": 1, "data": 1}

        # Mock 설정
        mock_post.return_value = mock_response

        # 좌석 예약 요청
        seat_id = 123
        time_minutes = 30
        status, message = self.api.book_seat(seat_id, time_minutes)

        # 결과 검증
        self.assertEqual(status, BookingStatus.SUCCESS)
        self.assertEqual(message, "SUCCESS")

        # 올바른 요청이 전송되었는지 확인
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "libraries/seat")
        self.assertEqual(kwargs["json_data"]["seatId"], seat_id)
        self.assertEqual(kwargs["json_data"]["time"], time_minutes)

    @patch("kgu_library.library.http_client.LibraryHTTPClient.post")
    def test_book_seat_failure(self, mock_post):
        """좌석 예약 실패 테스트"""
        # Mock 응답 데이터 (이미 다른 좌석 사용 중)
        mock_response = {"success": True, "code": 6, "status": 6, "data": 6}

        # Mock 설정
        mock_post.return_value = mock_response

        # 좌석 예약 요청
        seat_id = 123
        status, message = self.api.book_seat(seat_id)

        # 결과 검증
        self.assertEqual(status, BookingStatus.USING_ANOTHER_SEAT)
        self.assertEqual(message, "USING_ANOTHER_SEAT")

    @patch("kgu_library.library.http_client.LibraryHTTPClient.post")
    def test_cancel_seat_success(self, mock_post):
        """좌석 예약 취소 성공 테스트"""
        # Mock 응답 데이터
        mock_response = {"success": True, "data": True}

        # Mock 설정
        mock_post.return_value = mock_response

        # 좌석 취소 요청
        seat_id = 123
        result = self.api.cancel_seat(seat_id)

        # 결과 검증
        self.assertTrue(result)

        # 올바른 요청이 전송되었는지 확인
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], f"libraries/leave/{seat_id}")
        self.assertEqual(kwargs["json_data"], {})

    @patch("kgu_library.library.http_client.LibraryHTTPClient.post")
    def test_cancel_seat_failure(self, mock_post):
        """좌석 예약 취소 실패 테스트"""
        # Mock 응답 데이터
        mock_response = {"success": False, "error": "취소 실패"}

        # Mock 설정
        mock_post.return_value = mock_response

        # 좌석 취소 요청
        seat_id = 123
        result = self.api.cancel_seat(seat_id)

        # 결과 검증
        self.assertFalse(result)

    @patch("kgu_library.library.http_client.LibraryHTTPClient.get")
    def test_get_areas(self, mock_get):
        """영역 목록 조회 테스트"""
        # Mock 응답 데이터
        mock_response = {
            "code": 1,
            "status": 200,
            "message": "SUCCESS",
            "success": True,
            "data": [
                {
                    "code": 19,
                    "name": "제1열람실_충정관 2F",
                    "noteBookYN": "Y",
                    "keyboardYN": "N",
                    "talkYN": "N",
                    "startTm": "0600",
                    "endTm": "0000",
                    "wkStartTm": "0600",
                    "wkEndTm": "0000",
                    "cnt": 56,
                    "available": 56,
                    "inUse": 0,
                    "bgImg": "/resources/image/layout/seoul/1open.jpg",
                    "previewImg": "/resources/image/seoul/1open.png",
                    "miniMapImg": "/resources/image/minimap/seoul/1open.png",
                },
                {
                    "code": 20,
                    "name": "제2열람실_본관 3F",
                    "noteBookYN": "Y",
                    "keyboardYN": "N",
                    "talkYN": "N",
                    "startTm": "0600",
                    "endTm": "0000",
                    "wkStartTm": "0600",
                    "wkEndTm": "0000",
                    "cnt": 50,
                    "available": 50,
                    "inUse": 0,
                    "bgImg": "/resources/image/layout/seoul/2open.jpg",
                    "previewImg": "/resources/image/seoul/2open.png",
                    "miniMapImg": "/resources/image/minimap/seoul/2open.png",
                },
            ],
        }

        # Mock 설정
        mock_get.return_value = mock_response

        # 영역 목록 조회 요청
        library_id = 1
        result = self.api.get_areas(library_id)

        # 결과 검증
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], 19)
        self.assertEqual(result[0]["name"], "제1열람실_충정관 2F")
        self.assertEqual(result[1]["id"], 20)
        self.assertEqual(result[1]["name"], "제2열람실_본관 3F")
        self.assertEqual(result[0]["total_seats"], 56)
        self.assertEqual(result[0]["available"], 56)
        self.assertEqual(result[0]["in_use"], 0)
        self.assertEqual(result[0]["note_book_yn"], "Y")
        self.assertEqual(result[0]["keyboard_yn"], "N")
        self.assertEqual(result[0]["talk_yn"], "N")
        self.assertEqual(result[0]["start_time"], "0600")
        self.assertEqual(result[0]["end_time"], "0000")

        # 올바른 요청이 전송되었는지 확인
        mock_get.assert_called_with(f"libraries/lib-status/{library_id}")

    @patch("kgu_library.library.http_client.LibraryHTTPClient.get")
    def test_get_available_seats(self, mock_get):
        """사용 가능한 좌석 목록 조회 테스트"""
        # Mock 응답 데이터
        mock_response = {
            "code": 1,
            "status": 200,
            "message": "SUCCESS",
            "success": True,
            "data": [
                {
                    "code": 101,
                    "name": "A-101",
                    "status": "available",
                    "disabled": False,
                    "isActive": True,
                    "x": 100,
                    "y": 200,
                    "width": 30,
                    "height": 30,
                    "direction": 0,
                    "area": {"code": 19, "name": "제1열람실_충정관 2F"},
                    "seatTime": None,
                    "checkIn": None,
                    "endTime": None,
                    "userName": None,
                    "userId": None,
                    "isNotebook": False,
                    "isDisabled": False,
                    "isFixedSeat": False,
                },
                {
                    "code": 102,
                    "name": "A-102",
                    "status": "available",
                    "disabled": False,
                    "isActive": True,
                    "x": 140,
                    "y": 200,
                    "width": 30,
                    "height": 30,
                    "direction": 0,
                    "area": {"code": 19, "name": "제1열람실_충정관 2F"},
                    "seatTime": None,
                    "checkIn": None,
                    "endTime": None,
                    "userName": None,
                    "userId": None,
                    "isNotebook": False,
                    "isDisabled": False,
                    "isFixedSeat": False,
                },
                {
                    "code": 103,
                    "name": "A-103",
                    "status": "in_use",
                    "disabled": False,
                    "isActive": True,
                    "x": 180,
                    "y": 200,
                    "width": 30,
                    "height": 30,
                    "direction": 0,
                    "area": {"code": 19, "name": "제1열람실_충정관 2F"},
                    "seatTime": "2023-04-01 10:00:00",
                    "checkIn": "2023-04-01 10:00:00",
                    "endTime": "2023-04-01 12:00:00",
                    "userName": "홍길동",
                    "userId": "202300000",
                    "isNotebook": False,
                    "isDisabled": False,
                    "isFixedSeat": False,
                },
            ],
        }

        # Mock 설정
        mock_get.return_value = mock_response

        # 좌석 목록 조회 요청
        area_id = 19
        result = self.api.get_available_seats(area_id)

        # 결과 검증
        self.assertEqual(len(result), 2)  # 사용 중인 좌석(A-103)은 제외됨
        self.assertEqual(result[0]["id"], 101)
        self.assertEqual(result[0]["name"], "A-101")
        self.assertEqual(result[0]["area_name"], "제1열람실_충정관 2F")
        self.assertEqual(result[0]["x"], 100)
        self.assertEqual(result[0]["y"], 200)
        self.assertEqual(result[1]["id"], 102)
        self.assertEqual(result[1]["name"], "A-102")

        # 올바른 요청이 전송되었는지 확인
        mock_get.assert_called_with(f"libraries/seats/{area_id}")


if __name__ == "__main__":
    unittest.main()
