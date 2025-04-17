"""
KGU Attendance API 패키지

경기대학교 전자출결 시스템 API 라이브러리
"""

from .api import AttendanceAPI
from .http_client import AttendanceHTTPClient
from .enums import AttendanceStatus, LectureStatus, QRCodeStatus
from .exceptions import (
    AttendanceAPIError,
    AttendanceError,
    LoginError,
    QRCodeError,
    APIResponseError,
    SessionError,
    NotLoggedInError,
)

__all__ = [
    # API 클래스
    "AttendanceAPI",
    "AttendanceHTTPClient",
    # 열거형
    "AttendanceStatus",
    "LectureStatus",
    "QRCodeStatus",
    # 예외 클래스
    "AttendanceAPIError",
    "AttendanceError",
    "LoginError",
    "QRCodeError",
    "APIResponseError",
    "SessionError",
    "NotLoggedInError",
]

__version__ = "0.1.0"
