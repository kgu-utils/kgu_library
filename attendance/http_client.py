"""
전자출결 시스템과 통신하기 위한 HTTP 클라이언트

경기대학교 전자출결 시스템 API와 통신하기 위한 HTTP 클라이언트 클래스입니다.
"""

import json
import logging
import re
import time
import urllib.parse
from typing import Dict, Any, Optional, Union
from urllib.parse import urljoin

import requests

from .exceptions import (
    HttpClientError,
    LoginError,
    ResponseError,
)
from kgu_library.core.crypto import (
    hex_comma_str_to_bytes,
    bytes_to_hex_comma_str,
    SeedCbcCipher,
)

logger = logging.getLogger(__name__)

# 디버그 모드 설정 (디버그 로그 출력 여부)
DEBUG_MODE = False

# 경기대학교 전자출결 API 기본 URL
API_BASE_URL = "https://attend.kyonggi.ac.kr/attend/"
USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 SAI/31.1"


# 디버그 로그 출력 함수
def debug_log(message):
    if DEBUG_MODE:
        print(message)


class AttendanceHTTPClient:
    """경기대학교 전자출결 시스템 HTTP 클라이언트"""

    def __init__(self):
        """AttendanceHTTPClient 초기화"""
        self.session = requests.Session()
        self.base_url = API_BASE_URL
        self._is_logged_in = False
        self._token = None
        self.device_id = "Android"
        self.mac_id = "Android"
        self.mac_name = ""
        self.user_id = None
        self.user_name = None

    @property
    def is_logged_in(self) -> bool:
        """
        로그인 상태 확인

        Returns:
            로그인 상태 여부
        """
        return self._is_logged_in

    def login(self, user_id: str, password: str) -> Dict[str, Any]:
        """
        사용자 계정으로 로그인합니다.

        Args:
            user_id: 사용자 ID(학번)
            password: 비밀번호

        Returns:
            로그인 성공 시 반환되는 사용자 정보

        Raises:
            LoginError: 로그인 실패 시
        """
        try:
            # 디버깅을 위한 로그 추가
            debug_log(
                f"[DEBUG] 로그인 시작: user_id={user_id}, password={'*' * len(password) if password else None}"
            )
            logger.info(f"사용자 '{user_id}'로 로그인 시도 중...")

            self.user_id = user_id

            # URL 구성
            login_url = self.determine_server_url(user_id) + "rb_login.php"
            debug_log(f"[DEBUG] 로그인 URL: {login_url}")

            # 요청 데이터 준비
            login_data = {
                "duser_id": user_id,
                "duser_pw": urllib.parse.quote(password),  # URL 인코딩
                "device_id": self.device_id,
                "device_gubun": "Android",
                "mac_id": self.mac_id,
                "mac_name": urllib.parse.quote(
                    self.mac_name if self.mac_name else user_id
                ),
                "receive": "1.0.0-Python-1.0",  # 앱 버전, 디바이스 모델, OS 버전
            }
            debug_log(
                f"[DEBUG] 로그인 데이터: {json.dumps(login_data, ensure_ascii=False)}"
            )

            # 데이터 암호화
            encrypted_data = self.sencrypt(json.dumps(login_data))
            debug_log(
                f"[DEBUG] 암호화된 데이터 길이: {len(encrypted_data) if encrypted_data else 0}"
            )

            # 요청 파라미터 설정
            params = {"key": encrypted_data}

            # 로그인 요청 보내기
            debug_log(f"[DEBUG] 로그인 요청 전송 시작")
            response = self.session.post(login_url, data=params)
            debug_log(f"[DEBUG] 응답 상태 코드: {response.status_code}")
            debug_log(f"[DEBUG] 응답 헤더: {dict(response.headers)}")
            debug_log(f"[DEBUG] 응답 내용 (처음 100자): {response.text[:100]}")

            # 응답 확인
            if response.status_code == 200:
                # 응답 처리
                debug_log(f"[DEBUG] 응답 처리 시작")
                result = self.process_login_response(response.text)
                debug_log(
                    f"[DEBUG] 로그인 처리 결과: {json.dumps(result, ensure_ascii=False)}"
                )
                return result
            else:
                logger.error(f"로그인 실패: HTTP 상태 코드 {response.status_code}")
                raise LoginError(f"HTTP 오류: {response.status_code}")

        except Exception as e:
            logger.error(f"로그인 중 예외 발생: {str(e)}")
            debug_log(f"[DEBUG] 로그인 중 예외 발생: {type(e).__name__}: {str(e)}")
            raise LoginError(f"로그인 중 예외 발생: {str(e)}")

    def process_login_response(self, response_text):
        """로그인 응답 처리"""
        try:
            # 디버깅을 위한 로그 추가
            debug_log(f"[DEBUG] 응답 데이터 (처음 100자): {response_text[:100]}")

            # 로그인 응답 복호화 및 처리
            decrypted_response = self.sdecrypt(response_text)
            debug_log(f"[DEBUG] 복호화된 응답 (처음 100자): {decrypted_response[:100]}")

            response_json = json.loads(decrypted_response)
            debug_log(
                f"[DEBUG] 응답 JSON: {json.dumps(response_json, ensure_ascii=False)}"
            )

            # 로그인 성공 여부 확인
            if "xidedu" in response_json and response_json["xidedu"]["xmsg"] == "Ok":
                # 사용자 정보 저장
                xidedu_info = response_json["xidedu"]
                xuser_info = response_json.get("xuser", {})
                logger.info(f"로그인 성공: {xidedu_info['xmsg']}")

                # 디버깅
                debug_log(
                    f"[DEBUG] xidedu 정보: {json.dumps(xidedu_info, ensure_ascii=False)}"
                )
                debug_log(
                    f"[DEBUG] xuser 정보: {json.dumps(xuser_info, ensure_ascii=False)}"
                )

                # 사용자 정보 저장 - xuser 필드에서 정보 추출
                self.user_name = xuser_info.get("USER_NM", "")
                self._is_logged_in = True
                self._token = xuser_info.get("USER_ID", "")
                student_id = xuser_info.get("USER_ID", "")

                return {
                    "success": True,
                    "user_id": xuser_info.get("USER_ID", ""),
                    "user_name": xuser_info.get("USER_NM", ""),
                    "student_id": student_id,
                    "department": xuser_info.get("DEPT_NM", ""),
                    "grade": xuser_info.get("GRADE", ""),
                }
            else:
                error_msg = response_json.get("xidedu", {}).get(
                    "xmsg", "알 수 없는 오류"
                )
                logger.error(f"로그인 실패: {error_msg}")
                debug_log(f"[DEBUG] 로그인 실패 메시지: {error_msg}")
                return {"success": False, "error": error_msg}
        except Exception as e:
            logger.error(f"로그인 응답 처리 중 오류 발생: {e}")
            debug_log(f"[DEBUG] 로그인 응답 처리 중 예외: {type(e).__name__}: {str(e)}")
            return {"success": False, "error": str(e)}

    def determine_server_url(self, user_id):
        """사용자 ID에 따라 서버 URL 결정"""
        sitename = "kyonggi"
        test_patterns = [
            sitename.lower() + "prof",
            sitename.lower() + "stud1",
            sitename.lower() + "stud2",
            sitename.lower() + "stud3",
            sitename.lower() + "stud4",
            sitename.lower() + "stud5",
            sitename.lower() + "stud6",
            sitename.lower() + "stud7",
            sitename.lower() + "stud8",
            sitename.lower() + "stud9",
            sitename.lower() + "stud10",
        ]

        if user_id in test_patterns:
            return "http://story.xidsys.co.kr:9090/attend/"
        else:
            return self.base_url

    def logout(self) -> None:
        """로그아웃 처리"""
        if self._is_logged_in:
            # 세션 쿠키 삭제 및 세션 초기화
            self.session.cookies.clear()
            self._is_logged_in = False
            self._token = None
            self.user_id = None
            self.user_name = None
            logger.info("로그아웃 완료")

    def sencrypt(self, plaintext):
        """문자열 암호화"""
        try:
            # 암호화 키와 IV
            key_str = "80,E3,4F,8F,08,10,70,F1,E9,F3,94,37,0A,D4,05,89"
            iv_str = "20,8D,66,A7,30,A8,1A,81,6F,BA,D9,FA,36,10,25,01"

            # 16진수 문자열을 바이트 배열로 변환
            key = hex_comma_str_to_bytes(key_str)
            iv = hex_comma_str_to_bytes(iv_str)

            # SeedCbcCipher 클래스 사용
            cipher = SeedCbcCipher(key=key, iv=iv)
            encrypted_data = cipher.encrypt(plaintext.encode("utf-8"))
            return encrypted_data.hex()
        except Exception as e:
            logger.error(f"암호화 오류: {e}")
            return ""

    def sdecrypt(self, ciphertext):
        """암호화된 문자열 복호화"""
        try:
            # 암호화 키와 IV
            key_str = "80,E3,4F,8F,08,10,70,F1,E9,F3,94,37,0A,D4,05,89"
            iv_str = "20,8D,66,A7,30,A8,1A,81,6F,BA,D9,FA,36,10,25,01"

            # 16진수 문자열을 바이트 배열로 변환
            key = hex_comma_str_to_bytes(key_str)
            iv = hex_comma_str_to_bytes(iv_str)
            encrypted_data = bytes.fromhex(ciphertext.strip())

            # SeedCbcCipher 클래스 사용
            cipher = SeedCbcCipher(key=key, iv=iv)
            decrypted_data = cipher.decrypt(encrypted_data)
            return decrypted_data.decode("utf-8")
        except Exception as e:
            logger.error(f"복호화 오류: {e}")
            return ""

    def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        GET 요청 수행

        Args:
            endpoint: API 엔드포인트
            params: 요청 파라미터

        Returns:
            API 응답

        Raises:
            HttpClientError: HTTP 요청 실패 시
            ResponseError: API 응답 처리 실패 시
        """
        url = urljoin(self.base_url, endpoint)
        try:
            logger.debug(f"GET 요청: {url}, 파라미터: {params}")
            response = self.session.get(url, params=params)
            return self._process_response(response)
        except Exception as e:
            logger.error(f"GET 요청 실패: {url}, 오류: {str(e)}")
            raise HttpClientError(f"GET 요청 실패: {str(e)}")

    def post(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        POST 요청 수행

        Args:
            endpoint: API 엔드포인트
            data: 요청 데이터

        Returns:
            API 응답

        Raises:
            HttpClientError: HTTP 요청 실패 시
            ResponseError: API 응답 처리 실패 시
        """
        url = urljoin(self.base_url, endpoint)
        try:
            logger.debug(f"POST 요청: {url}, 데이터: {data}")

            # 데이터 암호화
            if data:
                encrypted_data = self.sencrypt(json.dumps(data))
                params = {"key": encrypted_data}
                response = self.session.post(url, data=params)
            else:
                response = self.session.post(url)

            return self._process_response(response)
        except Exception as e:
            logger.error(f"POST 요청 실패: {url}, 오류: {str(e)}")
            raise HttpClientError(f"POST 요청 실패: {str(e)}")

    def _process_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        HTTP 응답 처리

        Args:
            response: HTTP 응답 객체

        Returns:
            처리된 API 응답 데이터

        Raises:
            ResponseError: 응답 처리 실패 시
        """
        try:
            # HTTP 상태 코드 확인
            response.raise_for_status()

            # 응답 내용이 JSON인지 확인
            content_type = response.headers.get("Content-Type", "")
            if "application/json" in content_type:
                return response.json()
            else:
                # 복호화 시도
                try:
                    decrypted_text = self.sdecrypt(response.text)
                    return json.loads(decrypted_text)
                except:
                    # JSON이 아닌 경우, 텍스트 응답을 JSON 형식으로 파싱 시도
                    text = response.text.strip()
                    try:
                        # JSON 문자열 형태인지 확인 후 파싱
                        return json.loads(text)
                    except json.JSONDecodeError:
                        # JSON 파싱 실패 시 응답 텍스트 반환
                        return {"text": text}

        except requests.HTTPError as e:
            logger.error(f"HTTP 오류: {str(e)}, 상태 코드: {response.status_code}")
            raise ResponseError(
                f"HTTP 오류: {str(e)}, 상태 코드: {response.status_code}"
            )

    def _perform_user_search(self, request_data):
        """
        사용자 검색 내부 공통 로직

        Args:
            request_data: 검색 요청 데이터

        Returns:
            검색 결과 목록
        """
        if not self._is_logged_in:
            logger.error("로그인이 필요합니다.")
            return []

        # 검색 URL 설정
        search_url = self.determine_server_url(self.user_id) + "e_c_new/find_friend"

        # 데이터 암호화
        encrypted_data = self.sencrypt(json.dumps(request_data))

        # 요청 파라미터 설정
        params = {"key": encrypted_data}

        # POST 요청 보내기
        response = self.session.post(search_url, data=params)

        # 응답 확인
        if response.status_code == 200:
            try:
                # 결과 처리
                result = self.sdecrypt(response.text)
                result_json = json.loads(result)

                # 'result' -> 'find_friend'에서 검색 결과를 가져옴
                if "result" in result_json and "find_friend" in result_json["result"]:
                    return result_json["result"]["find_friend"]
                else:
                    logger.error("검색 결과가 없거나 형식이 올바르지 않습니다.")
                    return []
            except Exception as e:
                logger.error(f"응답 처리 중 오류 발생: {e}")
                return []
        else:
            logger.error(f"요청 실패: HTTP 상태 코드 {response.status_code}")
            return []

    def search_user_by_id(self, student_id):
        """
        학번으로 사용자 검색

        Args:
            student_id: 검색할 학번

        Returns:
            검색 결과 목록
        """
        # 학번으로 검색할 경우 sugang_student_id 키 사용
        request_data = {"sugang_student_id": student_id}
        return self._perform_user_search(request_data)

    def search_user_by_name(self, student_name):
        """
        이름으로 사용자 검색

        Args:
            student_name: 검색할 이름

        Returns:
            검색 결과 목록
        """
        # 이름으로 검색할 경우 sugang_student_name 키 사용
        request_data = {"sugang_student_name": student_name}
        return self._perform_user_search(request_data)

    def send_friend_request(self, user_info_num):
        """친구 요청 보내기"""
        if not self._is_logged_in:
            logger.error("로그인이 필요합니다.")
            return False

        # 정수형인 경우 문자열로 변환
        if isinstance(user_info_num, int):
            user_info_num = str(user_info_num)

        # 친구 요청 URL 설정
        request_url = self.determine_server_url(self.user_id) + "e_c_new/ask_consent"

        # 요청 데이터 준비
        request_data = {"sugang_user_info_num": user_info_num}

        # 데이터 암호화
        encrypted_data = self.sencrypt(json.dumps(request_data))

        # 요청 파라미터 설정
        params = {"key": encrypted_data}

        # POST 요청 보내기
        response = self.session.post(request_url, data=params)

        # 응답 확인
        if response.status_code == 200:
            try:
                # 응답 데이터 복호화 및 처리
                result = self.sdecrypt(response.text)
                result_json = json.loads(result)

                if "xidedu" in result_json and result_json["xidedu"]["xmsg"] == "Ok":
                    logger.info("친구 요청이 성공적으로 전송되었습니다.")
                    return True
                else:
                    error_msg = result_json.get("xidedu", {}).get(
                        "xmsg", "알 수 없는 오류"
                    )
                    logger.error(f"친구 요청 전송 실패: {error_msg}")
                    return False
            except Exception as e:
                logger.error(f"응답 처리 중 오류 발생: {e}")
                return False
        else:
            logger.error(f"요청 실패: HTTP 상태 코드 {response.status_code}")
            return False
