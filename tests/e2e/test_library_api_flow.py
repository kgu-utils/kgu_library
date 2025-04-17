"""
도서관 API e2e 테스트
"""

import pytest


class TestLibraryApiFlow:
    """도서관 API e2e 테스트 클래스"""

    def test_login(self, library_client, test_config, skip_real_api_tests):
        """로그인 테스트"""
        # 실제 API 테스트를 건너뛰는지 확인
        if skip_real_api_tests:
            pytest.skip("실제 API 테스트가 비활성화되어 있습니다.")

        # 테스트 계정 정보 가져오기
        credentials = test_config["credentials"]
        user_id = credentials["user_id"]
        password = credentials["password"]

        # 유효한 자격 증명이 없으면 테스트 건너뛰기
        if not user_id or not password:
            pytest.skip("테스트 계정 정보가 환경 변수에 설정되어 있지 않습니다.")

        # 로그인 요청
        login_result = library_client.login(user_id, password)

        # 결과 검증
        assert login_result is True
        print(f"도서관 시스템 로그인 성공: {user_id}")

    def test_get_areas(self, authenticated_library_client, skip_real_api_tests):
        """구역 목록 조회 테스트"""
        # 실제 API 테스트를 건너뛰는지 확인
        if skip_real_api_tests:
            pytest.skip("실제 API 테스트가 비활성화되어 있습니다.")

        # 구역 목록 조회
        areas = authenticated_library_client.get_areas()

        # 결과 검증
        assert areas is not None
        assert len(areas) > 0

        # 결과 출력
        print(f"{len(areas)}개의 구역을 찾았습니다:")
        for area in areas:
            print(
                f"- {area['name']}: 총 {area['total_seats']}석, 가용 {area['available']}석"
            )
            print(
                f"  노트북: {area['note_book_yn']}, 키보드: {area['keyboard_yn']}, 대화: {area['talk_yn']}"
            )

    def test_get_available_seats(
        self, authenticated_library_client, skip_real_api_tests
    ):
        """사용 가능한 좌석 목록 조회 테스트"""
        # 실제 API 테스트를 건너뛰는지 확인
        if skip_real_api_tests:
            pytest.skip("실제 API 테스트가 비활성화되어 있습니다.")

        # 구역 목록 조회 먼저 수행
        areas = authenticated_library_client.get_areas()
        if not areas:
            pytest.skip("조회 가능한 구역이 없습니다.")

        # 첫 번째 구역의 좌석 목록 조회
        area_id = areas[0]["id"]
        available_seats = authenticated_library_client.get_available_seats(area_id)

        # 결과 검증 (사용 가능한 좌석이 없어도 목록 자체는 반환됨)
        assert available_seats is not None

        # 결과 출력
        print(
            f"구역 {area_id}에서 {len(available_seats)}개의 사용 가능한 좌석을 찾았습니다:"
        )
        for i, seat in enumerate(available_seats[:5]):  # 처음 5개만 출력
            print(f"- {seat['name']} (ID: {seat['id']})")

        if len(available_seats) > 5:
            print(f"  ... 그 외 {len(available_seats) - 5}개")

    def test_check_my_status(self, authenticated_library_client, skip_real_api_tests):
        """내 좌석 상태 조회 테스트"""
        # 실제 API 테스트를 건너뛰는지 확인
        if skip_real_api_tests:
            pytest.skip("실제 API 테스트가 비활성화되어 있습니다.")

        # 내 좌석 상태 조회
        seat_info = authenticated_library_client.check_my_status()

        # 결과 출력 (예약된 좌석이 없어도 됨)
        if seat_info:
            print(
                f"현재 예약된 좌석: {seat_info.get('seatName')} (ID: {seat_info.get('seatId')})"
            )
            print(f"구역: {seat_info.get('areaName')}")
        else:
            print("현재 예약된 좌석이 없습니다.")

    def test_book_and_cancel_seat(
        self, authenticated_library_client, skip_real_api_tests
    ):
        """좌석 예약 및 취소 테스트 (옵션)"""
        # 실제 API 테스트를 건너뛰는지 확인
        if skip_real_api_tests:
            pytest.skip("실제 API 테스트가 비활성화되어 있습니다.")

        # 실제 예약 테스트는 실행하지 않음 (선택적으로 실행)
        pytest.skip("실제 좌석 예약/취소 테스트는 기본적으로 비활성화되어 있습니다.")

        # 구역 목록 조회
        areas = authenticated_library_client.get_areas()
        if not areas:
            pytest.skip("조회 가능한 구역이 없습니다.")

        # 첫 번째 구역의 좌석 목록 조회
        area_id = areas[0]["id"]
        available_seats = authenticated_library_client.get_available_seats(area_id)

        if not available_seats:
            pytest.skip(f"구역 {area_id}에 사용 가능한 좌석이 없습니다.")

        # 첫 번째 사용 가능한 좌석 선택
        seat_id = available_seats[0]["id"]

        # 현재 상태 확인
        current_seat = authenticated_library_client.check_my_status()
        if current_seat:
            # 이미 예약된 좌석이 있으면 취소
            seat_id_to_cancel = current_seat.get("seatId")
            cancel_result = authenticated_library_client.cancel_seat(seat_id_to_cancel)
            assert cancel_result is True
            print(f"기존 좌석 {seat_id_to_cancel} 취소 완료")

        # 좌석 예약
        booking_result, message = authenticated_library_client.book_seat(
            seat_id, time_minutes=30
        )
        print(f"좌석 {seat_id} 예약 결과: {message}")

        # 예약 확인
        seat_info = authenticated_library_client.check_my_status()
        assert seat_info is not None
        assert seat_info.get("seatId") == seat_id

        # 예약 취소
        cancel_result = authenticated_library_client.cancel_seat(seat_id)
        assert cancel_result is True
        print(f"좌석 {seat_id} 취소 완료")
