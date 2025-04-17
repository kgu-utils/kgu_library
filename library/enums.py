"""
KGU Library API 열거형 클래스
"""

from enum import Enum


class BookingStatus(Enum):
    """좌석 예약 API 응답 상태 Enum"""

    SUCCESS = 1  # 예약 성공 (코드 1, 200)
    NO_SEATS_AVAILABLE = 2  # 빈 좌석 없음 (코드 2)
    OPERATION_TIME_EXCEEDED = 3  # 운영 시간 초과 (코드 3)
    DAILY_LIMIT_REACHED = 4  # 일일 배정 가능 횟수 초과 (코드 4)
    CURRENTLY_WAITING = 5  # 현재 대기자 상태 (코드 5)
    USING_ANOTHER_SEAT = 6  # 현재 다른 좌석 사용 중 (코드 6)
    SEAT_IN_USE = 7  # 해당 좌석 사용 중 (코드 7)
    USING_FACILITY = 8  # 시설물 이용 중 (코드 8)
    WAITING_FOR_SAME_SEAT_REASSIGNMENT = 9  # 동일좌석 재배정 대기중 (코드 9)
    CLOSED_NEXT_DAY = 20  # 다음날 휴관일 (코드 20)
    BEFORE_OPERATION_HOURS = 21  # 운영 시간 시작 전 (코드 21)
    SAME_SEAT_RESERVATION_RESTRICTED = 22  # 동일 좌석 재배정 불가 (30분 제한) (코드 22)
    USAGE_TIME_EXCEEDED = 23  # 사용 시간 초과 (코드 23)
    USER_RESTRICTED = 999  # 이용 제한된 사용자 (코드 999)
    USER_NOT_FOUND = 998  # 없는 유저 (코드 998)
    NO_PERMISSION = 997  # 이용 권한 없음 (코드 997)
    PERMIT_MESSAGE = 995  # 허가 메시지 (코드 995)
    CUSTOM_MESSAGE = 994  # 커스텀 메시지 (코드 994)
    INVALID_RESPONSE = 900  # 응답 형식이 올바르지 않음
    API_ERROR = 901  # API 오류 (success: false 또는 요청 실패)
    UNKNOWN_ERROR = 999  # 알 수 없는 상태 코드
    CONFIRMATION_FAILED = 902  # 예약 확인 실패


class SeatExtensionStatus(Enum):
    """좌석 연장 API 응답 상태 Enum"""

    SEAT_NOT_FOUND = 0  # 좌석을 찾을 수 없음 (case 0)
    EXTENSION_SUCCESSFUL = 1  # 연장 성공 (case 1)
    EXTENSION_NOT_ALLOWED = 2  # 연장 불가 (case 2)
    EXTENSION_LIMIT_REACHED = 3  # 연장 횟수 제한 (case 3)
    TIME_OVER = 4  # 시간 초과 (case 4)
    NOT_OPERATING_TIME = 5  # 운영 시간 아님 (case 5, 6)
    EXTENSION_TOO_EARLY = 7  # 너무 이른 연장 시도 (case 7)
    EXTENSION_ONLY_ON_PC = 8  # PC에서만 연장 가능 (case 8)
    DUPLICATE_FACILITY_USE = 9  # 다른 시설 이용 중복 (case 9)
    BEACON_RETRY = 10  # 비콘 재시도 필요 (case 10)
    OVER_EXTEND_LIMIT = 11  # 최대 연장 시간 초과 (case 11)
    UNKNOWN_ERROR = 100  # 알 수 없는 오류
    API_ERROR = 101  # API 호출 오류 (success: false 등)
    INVALID_RESPONSE = 102  # 잘못된 응답 형식
