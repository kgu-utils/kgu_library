"""
KGU Library HTTP 클라이언트 모듈
"""

import requests
import json
import urllib3
from typing import Dict, Any, Optional

from .exceptions import LibraryAPIError, APIResponseError

# SSL 경고 비활성화
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class LibraryHTTPClient:
    """경기대학교 도서관 시스템 HTTP 클라이언트"""

    BASE_URL = "https://libgate.kyonggi.ac.kr"

    def __init__(self):
        """HTTP 클라이언트 초기화"""
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "ko-KR,ko;q=0.9",
                "Origin": self.BASE_URL,
                "Pragma": "no-cache",
            }
        )
        self.session.verify = False

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict:
        """GET 요청 수행

        Args:
            endpoint: API 엔드포인트 (BASE_URL 이후)
            params: 요청 파라미터
            headers: 요청 헤더

        Returns:
            Dict: API 응답 JSON

        Raises:
            APIResponseError: API 요청 또는 응답 처리 중 오류 발생
        """
        if not headers:
            headers = {}

        # 기본 헤더
        default_headers = {
            "Host": "libgate.kyonggi.ac.kr",
            "Accept": "application/json, text/plain, */*",
            "Referer": f"{self.BASE_URL}/seat",
        }

        # 기본 헤더와 커스텀 헤더 병합
        merged_headers = {**default_headers, **headers}

        try:
            full_url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
            response = self.session.get(
                full_url, params=params, headers=merged_headers, timeout=10
            )

            if response.status_code == 200:
                try:
                    return response.json()
                except json.JSONDecodeError as e:
                    raise APIResponseError(
                        f"응답을 JSON으로 변환할 수 없습니다: {e}"
                    ) from e
            else:
                raise APIResponseError(
                    f"API 요청 실패: 상태 코드 {response.status_code}"
                )

        except requests.RequestException as e:
            raise APIResponseError(f"API 요청 오류: {e}") from e

    def post(
        self,
        endpoint: str,
        data: Any = None,
        json_data: Optional[Dict] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict:
        """POST 요청 수행

        Args:
            endpoint: API 엔드포인트 (BASE_URL 이후)
            data: 요청 데이터 (form-data)
            json_data: 요청 JSON 데이터
            headers: 요청 헤더

        Returns:
            Dict: API 응답 JSON

        Raises:
            APIResponseError: API 요청 또는 응답 처리 중 오류 발생
        """
        if not headers:
            headers = {}

        # 기본 헤더
        default_headers = {
            "Host": "libgate.kyonggi.ac.kr",
            "Accept": "application/json, text/plain, */*",
            "Referer": f"{self.BASE_URL}/seat",
        }

        # JSON 데이터인 경우 Content-Type 추가
        if json_data is not None:
            default_headers["Content-Type"] = "application/json"

        # 기본 헤더와 커스텀 헤더 병합
        merged_headers = {**default_headers, **headers}

        try:
            full_url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
            response = self.session.post(
                full_url, data=data, json=json_data, headers=merged_headers, timeout=10
            )

            if response.status_code == 200:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    # JSON 파싱에 실패했지만 상태 코드가 200인 경우, 빈 객체로 처리
                    return {"success": True}
            else:
                raise APIResponseError(
                    f"API 요청 실패: 상태 코드 {response.status_code}"
                )

        except requests.RequestException as e:
            raise APIResponseError(f"API 요청 오류: {e}") from e
