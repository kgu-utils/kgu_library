"""
e2e 테스트 설정 모듈
"""

import os
from typing import Dict, Any

from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()


def get_test_config() -> Dict[str, Any]:
    """테스트 설정 정보를 반환합니다.

    Returns:
        Dict[str, Any]: 테스트 설정 정보
    """
    return {
        "credentials": {
            "user_id": os.getenv("KGU_TEST_USER_ID"),
            "password": os.getenv("KGU_TEST_PASSWORD"),
        },
        "test_data": {
            "search_user_id": os.getenv("KGU_TEST_SEARCH_USER_ID", "202411000"),
        },
        "flags": {
            "skip_friend_request": os.getenv("KGU_SKIP_FRIEND_REQUEST", "true").lower()
            == "true",
            "skip_real_api_tests": os.getenv("KGU_SKIP_REAL_API_TESTS", "false").lower()
            == "true",
        },
    }


def has_valid_credentials() -> bool:
    """유효한 테스트 계정 정보가 설정되어 있는지 확인합니다.

    Returns:
        bool: 유효한 테스트 계정 정보가 설정되어 있는지 여부
    """
    config = get_test_config()
    credentials = config["credentials"]
    return credentials["user_id"] is not None and credentials["password"] is not None
