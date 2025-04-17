import pytest
from kgu_library.tests.e2e.config import get_test_config, has_valid_credentials
from kgu_library.library import LibraryAPIWrapper
from kgu_library.attendance import AttendanceAPI


@pytest.fixture(scope="session")
def test_config():
    """테스트 설정 정보를 제공하는 fixture"""
    return get_test_config()


@pytest.fixture(scope="session")
def skip_real_api_tests(test_config):
    """실제 API 테스트를 건너뛸지 여부를 제공하는 fixture"""
    return test_config["flags"]["skip_real_api_tests"]


@pytest.fixture(scope="session")
def test_search_user_id(test_config):
    """테스트에 사용할 검색 사용자 ID를 제공하는 fixture"""
    return test_config["test_data"]["search_user_id"]


@pytest.fixture(scope="session")
def library_client():
    """LibraryAPIWrapper 클라이언트 인스턴스를 제공하는 fixture"""
    return LibraryAPIWrapper()


@pytest.fixture(scope="session")
def kgu_client():
    """AttendanceAPI 클라이언트 인스턴스를 제공하는 fixture"""
    return AttendanceAPI()


@pytest.fixture(scope="session")
def authenticated_library_client(library_client, test_config, skip_real_api_tests):
    """인증된 LibraryAPIWrapper 인스턴스를 제공하는 fixture"""
    # 실제 API 테스트를 건너뛰는지 확인
    if skip_real_api_tests:
        pytest.skip("실제 API 테스트가 비활성화되어 있습니다.")

    # 유효한 자격 증명이 있는지 확인
    if not has_valid_credentials():
        pytest.skip("테스트 계정 정보가 환경 변수에 설정되어 있지 않습니다.")

    # 클라이언트에 로그인
    credentials = test_config["credentials"]
    user_id = credentials["user_id"]
    password = credentials["password"]

    # 로그인 시도
    login_success = library_client.login(user_id, password)

    if not login_success:
        pytest.skip("테스트 계정으로 로그인하지 못했습니다.")

    return library_client


@pytest.fixture(scope="session")
def authenticated_client(kgu_client, test_config, skip_real_api_tests):
    """인증된 KGUAttendanceClient 인스턴스를 제공하는 fixture"""
    # 실제 API 테스트를 건너뛰는지 확인
    if skip_real_api_tests:
        pytest.skip("실제 API 테스트가 비활성화되어 있습니다.")

    # 유효한 자격 증명이 있는지 확인
    if not has_valid_credentials():
        pytest.skip("테스트 계정 정보가 환경 변수에 설정되어 있지 않습니다.")

    # 로그인
    credentials = test_config["credentials"]
    user_id = credentials["user_id"]
    password = credentials["password"]

    try:
        login_result = kgu_client.login(user_id, password)
        # login_result가 None이 아니고 user_id가 포함되어 있으면 성공
        if login_result is None or "user_id" not in login_result:
            pytest.skip("테스트 계정으로 로그인하지 못했습니다.")
    except Exception as e:
        pytest.skip(f"로그인 중 오류 발생: {str(e)}")

    return kgu_client
