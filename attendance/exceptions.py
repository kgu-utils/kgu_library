"""
전자출결 시스템 API 관련 예외 모듈

경기대학교 전자출결 시스템과 통신 중 발생할 수 있는 예외 클래스들을 정의합니다.
"""

from typing import Optional


class AttendanceAPIError(Exception):
    """전자출결 API 관련 기본 예외 클래스"""

    def __init__(self, message: str = "전자출결 API 오류가 발생했습니다."):
        self.message = message
        super().__init__(self.message)


class AttendanceError(AttendanceAPIError):
    """전자출결 일반 오류"""

    def __init__(self, message: str = "전자출결 처리 중 오류가 발생했습니다."):
        super().__init__(message)


class HttpClientError(AttendanceAPIError):
    """HTTP 클라이언트 관련 예외"""

    def __init__(self, message: str = "HTTP 요청 중 오류가 발생했습니다."):
        super().__init__(message)


class ResponseError(AttendanceAPIError):
    """API 응답 처리 중 발생하는 예외"""

    def __init__(self, message: str = "API 응답 처리 중 오류가 발생했습니다."):
        super().__init__(message)


class APIResponseError(ResponseError):
    """API 응답 처리 중 발생하는 예외"""

    def __init__(self, message: str = "API 응답 처리 중 오류가 발생했습니다."):
        super().__init__(message)


class LoginError(AttendanceAPIError):
    """로그인 관련 예외"""

    def __init__(self, message: str = "로그인 중 오류가 발생했습니다."):
        super().__init__(message)


class SessionError(AttendanceAPIError):
    """세션 관련 예외"""

    def __init__(self, message: str = "세션이 유효하지 않습니다. 다시 로그인해주세요."):
        super().__init__(message)


class NotLoggedInError(SessionError):
    """로그인되지 않은 상태에서 인증이 필요한 요청 시 발생하는 예외"""

    def __init__(self, message: str = "로그인이 필요한 작업입니다."):
        super().__init__(message)


class InvalidArgumentError(AttendanceAPIError):
    """잘못된 인자가 전달되었을 때 발생하는 예외"""

    def __init__(self, message: str = "잘못된 인자가 전달되었습니다."):
        super().__init__(message)


class QrCodeError(AttendanceAPIError):
    """QR 코드 처리 중 발생하는 예외"""

    def __init__(self, message: str = "QR 코드 처리 중 오류가 발생했습니다."):
        super().__init__(message)


# QRCodeError는 QrCodeError의 별칭으로 유지 (하위 호환성)
QRCodeError = QrCodeError


class AttendanceDataError(AttendanceAPIError):
    """출결 데이터 처리 관련 예외"""

    def __init__(self, message: str = "출결 데이터 처리 중 오류가 발생했습니다."):
        super().__init__(message)
