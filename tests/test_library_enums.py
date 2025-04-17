"""
도서관 시스템 열거형 테스트 코드
"""

import unittest

from kgu_library.library.enums import BookingStatus, SeatExtensionStatus


class TestLibraryEnums(unittest.TestCase):
    """도서관 시스템 열거형 테스트 클래스"""

    def test_booking_status_values(self):
        """BookingStatus 열거형 값 테스트"""
        # 주요 상태 코드 값 검증
        self.assertEqual(BookingStatus.SUCCESS.value, 1)
        self.assertEqual(BookingStatus.NO_SEATS_AVAILABLE.value, 2)
        self.assertEqual(BookingStatus.OPERATION_TIME_EXCEEDED.value, 3)
        self.assertEqual(BookingStatus.DAILY_LIMIT_REACHED.value, 4)
        self.assertEqual(BookingStatus.CURRENTLY_WAITING.value, 5)
        self.assertEqual(BookingStatus.USING_ANOTHER_SEAT.value, 6)
        self.assertEqual(BookingStatus.SEAT_IN_USE.value, 7)
        self.assertEqual(BookingStatus.USING_FACILITY.value, 8)
        self.assertEqual(BookingStatus.WAITING_FOR_SAME_SEAT_REASSIGNMENT.value, 9)
        self.assertEqual(BookingStatus.CLOSED_NEXT_DAY.value, 20)
        self.assertEqual(BookingStatus.BEFORE_OPERATION_HOURS.value, 21)
        self.assertEqual(BookingStatus.SAME_SEAT_RESERVATION_RESTRICTED.value, 22)
        self.assertEqual(BookingStatus.USAGE_TIME_EXCEEDED.value, 23)
        self.assertEqual(BookingStatus.USER_RESTRICTED.value, 999)

    def test_booking_status_lookup(self):
        """BookingStatus 열거형 조회 테스트"""
        # 코드로 열거형 찾기
        self.assertEqual(BookingStatus(1), BookingStatus.SUCCESS)
        self.assertEqual(BookingStatus(6), BookingStatus.USING_ANOTHER_SEAT)
        self.assertEqual(BookingStatus(7), BookingStatus.SEAT_IN_USE)
        self.assertEqual(
            BookingStatus(22), BookingStatus.SAME_SEAT_RESERVATION_RESTRICTED
        )

        # 200도 성공으로 처리되는지 체크 (API 상 1과 200이 모두 사용됨)
        with self.assertRaises(ValueError):
            # 직접적인 200 매핑은 없음 (코드 내에서 변환 처리)
            BookingStatus(200)

    def test_invalid_booking_status(self):
        """잘못된 BookingStatus 열거형 조회 테스트"""
        # 존재하지 않는 코드로 조회 시 예외 발생
        with self.assertRaises(ValueError):
            BookingStatus(99999)

        with self.assertRaises(ValueError):
            BookingStatus(-1)

    def test_seat_extension_status_values(self):
        """SeatExtensionStatus 열거형 값 테스트"""
        # 주요 상태 코드 값 검증
        self.assertEqual(SeatExtensionStatus.SEAT_NOT_FOUND.value, 0)
        self.assertEqual(SeatExtensionStatus.EXTENSION_SUCCESSFUL.value, 1)
        self.assertEqual(SeatExtensionStatus.EXTENSION_NOT_ALLOWED.value, 2)
        self.assertEqual(SeatExtensionStatus.EXTENSION_LIMIT_REACHED.value, 3)
        self.assertEqual(SeatExtensionStatus.TIME_OVER.value, 4)
        self.assertEqual(SeatExtensionStatus.NOT_OPERATING_TIME.value, 5)
        self.assertEqual(SeatExtensionStatus.EXTENSION_TOO_EARLY.value, 7)
        self.assertEqual(SeatExtensionStatus.EXTENSION_ONLY_ON_PC.value, 8)
        self.assertEqual(SeatExtensionStatus.DUPLICATE_FACILITY_USE.value, 9)
        self.assertEqual(SeatExtensionStatus.BEACON_RETRY.value, 10)
        self.assertEqual(SeatExtensionStatus.OVER_EXTEND_LIMIT.value, 11)
        self.assertEqual(SeatExtensionStatus.UNKNOWN_ERROR.value, 100)
        self.assertEqual(SeatExtensionStatus.API_ERROR.value, 101)
        self.assertEqual(SeatExtensionStatus.INVALID_RESPONSE.value, 102)

    def test_seat_extension_status_lookup(self):
        """SeatExtensionStatus 열거형 조회 테스트"""
        # 코드로 열거형 찾기
        self.assertEqual(SeatExtensionStatus(0), SeatExtensionStatus.SEAT_NOT_FOUND)
        self.assertEqual(
            SeatExtensionStatus(1), SeatExtensionStatus.EXTENSION_SUCCESSFUL
        )
        self.assertEqual(
            SeatExtensionStatus(3), SeatExtensionStatus.EXTENSION_LIMIT_REACHED
        )
        self.assertEqual(SeatExtensionStatus(11), SeatExtensionStatus.OVER_EXTEND_LIMIT)

    def test_invalid_seat_extension_status(self):
        """잘못된 SeatExtensionStatus 열거형 조회 테스트"""
        # 존재하지 않는 코드로 조회 시 예외 발생
        with self.assertRaises(ValueError):
            SeatExtensionStatus(99999)

        with self.assertRaises(ValueError):
            SeatExtensionStatus(-1)

        # 5와 6은 모두 NOT_OPERATING_TIME 상태로 처리되지만,
        # enum에 정의된 것은 5뿐이므로 6은 예외 발생
        with self.assertRaises(ValueError):
            SeatExtensionStatus(6)


if __name__ == "__main__":
    unittest.main()
