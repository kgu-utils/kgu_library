"""
pytest 프레임워크를 이용한 e2e 테스트
"""

import pytest


class TestKGUClientPytest:
    """KGUAttendanceClient pytest 기반 e2e 테스트 클래스"""

    def test_login(self, kgu_client, test_config, skip_real_api_tests):
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
        login_result = kgu_client.login(user_id, password)

        # 결과 검증 (AttendanceAPI.login 메소드는 성공 시 사용자 정보를 직접 반환)
        assert login_result is not None
        assert "user_id" in login_result
        assert "user_name" in login_result

        print(f"로그인 성공: {login_result['user_name']} ({login_result['user_id']})")

        # 로그인 상태 검증
        assert kgu_client.is_logged_in is True

    def test_search_user(
        self, authenticated_client, test_search_user_id, skip_real_api_tests
    ):
        """사용자 검색 테스트"""
        # 실제 API 테스트를 건너뛰는지 확인
        if skip_real_api_tests:
            pytest.skip("실제 API 테스트가 비활성화되어 있습니다.")

        # 이미 로그인된 클라이언트로 사용자 검색
        search_results = authenticated_client.search_user(test_search_user_id)

        # 결과 검증
        assert search_results is not None

        # 검색 결과가 있을 수도, 없을 수도 있으므로 조건부 검증
        if len(search_results) > 0:
            print(f"사용자 검색 결과: {len(search_results)}명의 사용자를 찾았습니다.")
            for user in search_results:
                print(
                    f"이름: {user.get('sugang_student_name', '')}, ID: {user.get('sugang_student_id', '')}"
                )

            # 첫 번째 검색 결과 검증
            first_user = search_results[0]
            assert "sugang_user_info_num" in first_user
            assert "sugang_student_id" in first_user
            assert "sugang_student_name" in first_user
        else:
            print(f"ID {test_search_user_id}에 해당하는 사용자를 찾을 수 없습니다.")

    def test_friend_request(
        self,
        authenticated_client,
        test_search_user_id,
        test_config,
        skip_real_api_tests,
    ):
        """친구 요청 테스트"""
        # 실제 API 테스트를 건너뛰는지 확인
        if skip_real_api_tests:
            pytest.skip("실제 API 테스트가 비활성화되어 있습니다.")

        # 친구 요청 테스트 비활성화 여부 확인
        if test_config["flags"]["skip_friend_request"]:
            pytest.skip("친구 요청 테스트가 비활성화되어 있습니다.")

        # 사용자 검색
        search_results = authenticated_client.search_user(test_search_user_id)

        # 검색 결과가 없으면 테스트 건너뛰기
        if not search_results or len(search_results) == 0:
            pytest.skip(
                f"ID {test_search_user_id}에 해당하는 사용자를 찾을 수 없어 친구 요청 테스트를 건너뜁니다."
            )

        # 친구 요청 보내기
        user_info_num = str(
            search_results[0]["sugang_user_info_num"]
        )  # 명시적으로 문자열로 변환
        print(f"사용자 ID: {user_info_num}에게 친구 요청을 보냅니다...")

        friend_request_result = authenticated_client.send_friend_request(user_info_num)

        # 결과 검증
        assert friend_request_result is True
        print("친구 요청 보내기 성공")
