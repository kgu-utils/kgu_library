"""
KGU Library API 모듈
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple

from .enums import BookingStatus, SeatExtensionStatus
from .exceptions import BookingError, SeatError, APIResponseError, LoginError
from .http_client import LibraryHTTPClient


class LibraryAPIWrapper:
    """경기대학교 도서관 좌석 예약 시스템 API 래퍼"""

    def __init__(self):
        """API 래퍼 초기화"""
        self.client = LibraryHTTPClient()

    def login(self, user_id: str, name: str) -> bool:
        """도서관 시스템에 로그인

        Args:
            user_id: 사용자 ID
            name: 이름 (실제 이름이 아닌 ID를 입력해도 로그인 가능)

        Returns:
            bool: 로그인 성공 여부

        Raises:
            LoginError: 로그인 과정에서 오류 발생
        """
        try:
            # 사용자 ID에 0 패딩 추가 (12자리)
            user_id_padded = f"000000{user_id}"[-12:]

            # 로그인 요청 데이터 준비
            login_data = f"ID={user_id_padded}&STD_ID={user_id}&NAME={name}"

            # 헤더 설정
            login_headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": "https://library.kyonggi.ac.kr/",
            }

            # HTTP 클라이언트를 통해 로그인 요청 전송
            try:
                # POST 요청 직접 전송 (URL이 특별한 경로라서 post 메서드 대신 직접 호출)
                login_url = f"{self.client.BASE_URL}/login_library"
                login_response = self.client.session.post(
                    login_url,
                    data=login_data,
                    headers=login_headers,
                    allow_redirects=True,
                    timeout=10,
                )

                # 로그인 성공 여부 확인
                if login_response.status_code == 200:
                    # 응답이 JSON인지 확인
                    try:
                        result = login_response.json()
                        if result.get("success", False):
                            return True
                    except Exception:
                        # JSON이 아닌 경우에도 성공했을 수 있음 - 세션 쿠키를 확인
                        if any(
                            cookie.name == "CLI_ID"
                            for cookie in self.client.session.cookies
                        ):
                            return True

                return False
            except Exception as e:
                raise LoginError(f"로그인 요청 실패: {e}") from e

        except Exception as e:
            raise LoginError(f"로그인 과정 오류: {e}") from e

    def check_my_status(self) -> Optional[Dict]:
        """내 현재 예약 상태 확인하고 좌석 정보 반환

        Returns:
            Optional[Dict]: 좌석 정보 (없으면 None)

        Raises:
            APIResponseError: API 응답 처리 중 오류 발생
        """
        # 상태 확인 API 호출
        response = self.client.get("user/my-status")

        if response.get("success") and response.get("data"):
            data = response.get("data")

            # mySeat 정보가 있는지 확인
            seat_info = data.get("mySeat")
            if seat_info:
                return seat_info

        return None

    def book_seat(
        self, seat_id: int, time_minutes: int = 30
    ) -> Tuple[BookingStatus, str]:
        """좌석 예약하기

        Args:
            seat_id: 좌석 ID
            time_minutes: 예약 시간 (분 단위)

        Returns:
            Tuple[BookingStatus, str]: (상태 열거형, 상태 메시지) 튜플

        Raises:
            BookingError: 예약 과정에서 오류 발생
        """
        try:
            # 예약 요청 데이터
            json_data = {
                "seatId": seat_id,
                "time": time_minutes,
            }

            # 헤더 설정
            headers = {
                "Referer": f"{self.client.BASE_URL}/seat",
            }

            # POST 요청 수행
            response = self.client.post(
                "libraries/seat", json_data=json_data, headers=headers
            )

            # 기본 응답 검사 (success: false)
            if not response.get("success", False):
                return (
                    BookingStatus.API_ERROR,
                    f"API 오류: {response.get('message', '알 수 없는 오류')}",
                )

            # 코드 확인
            code = response.get("data")

            # 성공 코드 (1 또는 200) 특별 처리
            if (
                response.get("code") in [1, 200]
                and response.get("status") in [1, 200]
                and code in [1, 200]
            ):
                return BookingStatus.SUCCESS, "SUCCESS"

            try:
                # 직접 코드를 BookingStatus enum으로 변환
                status = BookingStatus(code)
                return status, status.name
            except ValueError:
                return BookingStatus.UNKNOWN_ERROR, f"UNKNOWN_ERROR (Code: {code})"

        except Exception as e:
            raise BookingError(f"좌석 예약 실패: {e}") from e

    def cancel_seat(self, seat_id: int) -> bool:
        """좌석 예약 취소

        Args:
            seat_id: 좌석 ID

        Returns:
            bool: 취소 성공 여부

        Raises:
            BookingError: 취소 과정에서 오류 발생
        """
        try:
            # 헤더 설정
            headers = {
                "Referer": f"{self.client.BASE_URL}/",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
            }

            # 취소 요청 데이터 (빈 객체로 전송)
            json_data = {}

            # POST 요청 수행
            response = self.client.post(
                f"libraries/leave/{seat_id}", json_data=json_data, headers=headers
            )

            # 에러 체크
            if "error" in response:
                return False

            # 성공 여부 반환
            return response.get("success", False)

        except Exception as e:
            raise BookingError(f"좌석 취소 과정 오류: {e}") from e

    def get_areas(self, library_id: int = 1) -> List[Dict]:
        """도서관 구역 정보 가져오기

        Args:
            library_id: 도서관 ID (기본값: 1 - 수원캠퍼스)

        Returns:
            List[Dict]: 구역 정보 목록

        Raises:
            APIResponseError: API 응답 처리 중 오류 발생
        """
        # 구역 정보 요청
        response = self.client.get(f"libraries/lib-status/{library_id}")

        if response.get("success") and response.get("data"):
            # API 응답에서 data 배열 가져오기
            areas_data = response.get("data")
            areas = []

            for area in areas_data:
                # 모든 필드를 직접 매핑
                area_info = {
                    # 기본 정보
                    "id": area.get("code"),
                    "code": area.get("code"),
                    "name": area.get("name"),
                    "name_eng": area.get("nameEng"),
                    # 좌석 정보
                    "total_seats": area.get("cnt", 0),
                    "available": area.get("available", 0),
                    "in_use": area.get("inUse", 0),
                    "fix": area.get("fix", 0),
                    "disabled": area.get("disabled", 0),
                    "fixed_seat": area.get("fixedSeat", 0),
                    "normal": area.get("normal", 0),
                    "unavailable": area.get("unavailable", 0),
                    # 기능 허용 여부
                    "note_book_yn": area.get("noteBookYN"),
                    "keyboard_yn": area.get("keyboardYN"),
                    "talk_yn": area.get("talkYN"),
                    # 시간 설정
                    "sc_ck_mi": area.get("scCkMi"),  # 체크인 간격(분)
                    "max_mi": area.get("maxMi"),  # 최대 이용 시간(분)
                    "max_renew_mi": area.get("maxRenewMi"),  # 최대 연장 시간(분)
                    "start_time": area.get("startTm"),  # 운영 시작 시간
                    "end_time": area.get("endTm"),  # 운영 종료 시간
                    "week_start_time": area.get("wkStartTm"),  # 주중 운영 시작 시간
                    "week_end_time": area.get("wkEndTm"),  # 주중 운영 종료 시간
                    "week_setting": area.get("wkSetting"),  # 주간 설정
                    "week_time_use_setting": area.get(
                        "wkTimeUseSetting"
                    ),  # 주간 시간 이용 설정
                    "week_reserve_use_yn": area.get(
                        "wkRsrvUseYn"
                    ),  # 주간 예약 이용 여부
                    # 이미지 정보
                    "bg_image": area.get("bgImg"),  # 배경 이미지
                    "preview_image": area.get("previewImg"),  # 미리보기 이미지
                    "minimap_image": area.get("miniMapImg"),  # 미니맵 이미지
                    "minimap_lib_image": area.get(
                        "miniMapLibImg"
                    ),  # 미니맵 도서관 이미지
                    # 색상 정보
                    "color": area.get("color"),
                    # 휴일 정보
                    "day_off": area.get("dayOff"),
                    # 특별 이용 정보
                    "va_name": area.get("vaName"),  # 특별 이용명
                    "va_start_time": area.get("vaStartTime"),  # 특별 이용 시작 시간
                    "va_end_time": area.get("vaEndTime"),  # 특별 이용 종료 시간
                    "va_week_start_time": area.get(
                        "vaWkStartTime"
                    ),  # 특별 이용 주중 시작 시간
                    "va_week_end_time": area.get(
                        "vaWkEndTime"
                    ),  # 특별 이용 주중 종료 시간
                    "va_week_setting": area.get("vaWkSetting"),  # 특별 이용 주간 설정
                    "va_week_time_use_setting": area.get(
                        "vaWkTimeUseSetting"
                    ),  # 특별 이용 주간 시간 이용 설정
                    "va_week_reserve_use_yn": area.get(
                        "vaWkRsrvUseYn"
                    ),  # 특별 이용 주간 예약 이용 여부
                }

                areas.append(area_info)

            return areas
        else:
            raise APIResponseError(
                f"구역 정보를 가져오는데 실패했습니다: {response.get('message', '알 수 없는 오류')}"
            )

    def get_available_seats(self, area_id: int = 1) -> List[Dict]:
        """사용 가능한 좌석 목록 가져오기

        Args:
            area_id: 구역 ID

        Returns:
            List[Dict]: 사용 가능한 좌석 목록

        Raises:
            SeatError: 좌석 정보 조회 중 오류 발생
        """
        try:
            # 좌석 정보 요청
            response = self.client.get(f"libraries/seats/{area_id}")

            if response.get("success") and response.get("data"):
                seats_data = response.get("data")
                available_seats = []

                # 좌석 목록에서 사용 가능한 좌석만 필터링
                for seat in seats_data:
                    # seatTime이 null이면 예약 가능한 좌석
                    if seat.get("seatTime") is None:
                        # 모든 필드 매핑
                        seat_info = {
                            # 기본 정보
                            "id": seat.get("code"),
                            "code": seat.get("code"),
                            "name": seat.get("name"),
                            "status": seat.get("status"),
                            "disabled": seat.get("disabled"),
                            "is_active": seat.get("isActive"),
                            # 좌석 위치 정보
                            "x": seat.get("x"),
                            "y": seat.get("y"),
                            "width": seat.get("width"),
                            "height": seat.get("height"),
                            "direction": seat.get("direction"),
                            # 구역 정보
                            "area_id": seat.get("area", {}).get("code"),
                            "area_name": seat.get("area", {}).get("name", "알 수 없음"),
                            # 사용 정보
                            "seat_time": seat.get("seatTime"),
                            "check_in": seat.get("checkIn"),
                            "end_time": seat.get("endTime"),
                            "user_name": seat.get("userName"),
                            "user_id": seat.get("userId"),
                            # 추가 정보
                            "is_notebook": seat.get("isNotebook"),
                            "is_disabled": seat.get("isDisabled"),
                            "is_fixed_seat": seat.get("isFixedSeat"),
                        }

                        available_seats.append(seat_info)

                return available_seats
            else:
                raise SeatError(
                    f"좌석 정보를 가져오는데 실패했습니다: {response.get('message', '알 수 없는 오류')}"
                )

        except Exception as e:
            raise SeatError(f"좌석 정보 요청 오류: {e}") from e


# 이전 버전과의 호환성을 위해 LibraryAPI 이름으로 래퍼 클래스 제공
LibraryAPI = LibraryAPIWrapper
