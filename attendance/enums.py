"""
전자학생증 API 열거형 모듈
"""

from enum import Enum, IntEnum


class AttendanceStatus(IntEnum):
    """출석 상태 열거형"""

    PENDING = 0  # 처리 중
    PRESENT = 1  # 출석
    LATE = 2  # 지각
    ABSENT = 3  # 결석
    EXCUSED = 4  # 공결


class LectureStatus(IntEnum):
    """강의 상태 열거형"""

    SCHEDULED = 0  # 예정됨
    IN_PROGRESS = 1  # 진행 중
    COMPLETED = 2  # 완료됨


class QRCodeStatus(IntEnum):
    """QR 코드 상태 열거형"""

    VALID = 0  # 유효함
    EXPIRED = 1  # 만료됨
    INVALID = 2  # 유효하지 않음
