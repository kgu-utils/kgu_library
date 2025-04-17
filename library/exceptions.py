"""
KGU Library API 예외 클래스
"""


class LibraryAPIError(Exception):
    """KGU Library API 기본 예외 클래스"""

    pass


class LoginError(LibraryAPIError):
    """로그인 관련 예외"""

    pass


class BookingError(LibraryAPIError):
    """좌석 예약 관련 예외"""

    pass


class SeatError(LibraryAPIError):
    """좌석 정보 관련 예외"""

    pass


class APIResponseError(LibraryAPIError):
    """API 응답 관련 예외"""

    pass
