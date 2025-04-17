"""
전자출결 시스템 API 래퍼

경기대학교 전자출결 시스템 API를 사용하기 위한 래퍼 클래스
"""

import datetime
import json
import logging
import re
from typing import Dict, List, Any, Optional, Union, Tuple

from .exceptions import (
    AttendanceError,
    LoginError,
    NotLoggedInError,
    InvalidArgumentError,
    QrCodeError,
)
from .http_client import AttendanceHTTPClient

logger = logging.getLogger(__name__)


class AttendanceAPI:
    """
    경기대학교 전자출결 시스템 API 클래스

    전자출결 시스템의 HTTP API를 래핑하여 사용하기 쉽게 제공합니다.
    """

    def __init__(self):
        """AttendanceAPI 초기화"""
        self.client = AttendanceHTTPClient()
        self.user_info = None

    @property
    def is_logged_in(self) -> bool:
        """
        로그인 상태 확인

        Returns:
            로그인 상태 여부
        """
        return self.client.is_logged_in

    def login(self, user_id: str, password: str) -> Dict[str, Any]:
        """
        사용자 계정으로 로그인

        Args:
            user_id: 사용자 ID(학번)
            password: 비밀번호

        Returns:
            로그인 성공 시 반환되는 사용자 정보

        Raises:
            LoginError: 로그인 실패 시
        """
        try:
            result = self.client.login(user_id, password)

            # 성공 여부 확인
            if result.get("success", False):
                self.user_info = {
                    "user_id": result.get("user_id", ""),
                    "user_name": result.get("user_name", ""),
                    "student_id": result.get("student_id", ""),
                }
                return self.user_info
            else:
                error_msg = result.get("error", "알 수 없는 로그인 오류")
                raise LoginError(f"로그인 실패: {error_msg}")

        except Exception as e:
            if isinstance(e, LoginError):
                raise
            else:
                logger.exception("로그인 중 예외 발생")
                raise LoginError(f"로그인 중 예외 발생: {str(e)}")

    def logout(self) -> None:
        """
        로그아웃 처리

        Raises:
            AttendanceError: 로그아웃 실패 시
        """
        try:
            self.client.logout()
            self.user_info = None
        except Exception as e:
            logger.exception("로그아웃 중 예외 발생")
            raise AttendanceError(f"로그아웃 중 예외 발생: {str(e)}")

    def check_user_info(self) -> Dict[str, Any]:
        """
        현재 로그인된 사용자 정보 확인

        Returns:
            사용자 정보

        Raises:
            NotLoggedInError: 로그인되지 않은 경우
        """
        if not self.is_logged_in:
            raise NotLoggedInError("사용자 정보를 확인하려면 먼저 로그인하세요")

        return self.user_info

    def get_qr_code(self) -> Dict[str, Any]:
        """
        출석 QR 코드 정보 조회

        Returns:
            QR 코드 정보 (출석 키, 유효 시간 등)

        Raises:
            NotLoggedInError: 로그인되지 않은 경우
            QrCodeError: QR 코드 조회 실패 시
        """
        if not self.is_logged_in:
            raise NotLoggedInError("QR 코드를 조회하려면 먼저 로그인하세요")

        try:
            # QR 코드 URL 설정
            qr_url = (
                self.client.determine_server_url(self.user_info["user_id"])
                + "rb_qrcode.php"
            )

            # 요청 데이터 준비
            request_data = {"type": "qrcode"}

            # 암호화 및 요청
            encrypted_data = self.client.sencrypt(json.dumps(request_data))
            params = {"key": encrypted_data}

            # POST 요청 보내기
            response = self.client.session.post(qr_url, data=params)

            # 응답 확인
            if response.status_code == 200:
                result = self.client.sdecrypt(response.text)
                result_json = json.loads(result)

                if "xidedu" in result_json and result_json["xidedu"]["xmsg"] == "Ok":
                    qr_info = result_json["xidedu"]
                    return {
                        "qr_key": qr_info.get("qr_key", ""),
                        "validity": qr_info.get("validity", 60),  # 기본 60초
                        "timestamp": qr_info.get("timestamp", ""),
                    }
                else:
                    error_msg = result_json.get("xidedu", {}).get(
                        "xmsg", "알 수 없는 오류"
                    )
                    raise QrCodeError(f"QR 코드 조회 실패: {error_msg}")
            else:
                raise QrCodeError(
                    f"QR 코드 조회 실패: HTTP 상태 코드 {response.status_code}"
                )

        except Exception as e:
            if isinstance(e, QrCodeError):
                raise
            else:
                logger.exception("QR 코드 조회 중 예외 발생")
                raise QrCodeError(f"QR 코드 조회 중 예외 발생: {str(e)}")

    def get_attendance_list(
        self,
        from_date: Optional[Union[str, datetime.date]] = None,
        to_date: Optional[Union[str, datetime.date]] = None,
    ) -> List[Dict[str, Any]]:
        """
        출석 내역 조회

        Args:
            from_date: 조회 시작 날짜 (YYYY-MM-DD 형식의 문자열 또는 datetime.date 객체)
            to_date: 조회 종료 날짜 (YYYY-MM-DD 형식의 문자열 또는 datetime.date 객체)

        Returns:
            출석 내역 목록

        Raises:
            NotLoggedInError: 로그인되지 않은 경우
            InvalidArgumentError: 날짜 형식이 유효하지 않은 경우
            AttendanceError: 출석 내역 조회 실패 시
        """
        if not self.is_logged_in:
            raise NotLoggedInError("출석 내역을 조회하려면 먼저 로그인하세요")

        # 날짜 형식 변환
        if from_date:
            if isinstance(from_date, datetime.date):
                from_date = from_date.strftime("%Y-%m-%d")
            elif not re.match(r"^\d{4}-\d{2}-\d{2}$", from_date):
                raise InvalidArgumentError(
                    "from_date는 YYYY-MM-DD 형식의 문자열이어야 합니다"
                )

        if to_date:
            if isinstance(to_date, datetime.date):
                to_date = to_date.strftime("%Y-%m-%d")
            elif not re.match(r"^\d{4}-\d{2}-\d{2}$", to_date):
                raise InvalidArgumentError(
                    "to_date는 YYYY-MM-DD 형식의 문자열이어야 합니다"
                )

        try:
            # 현재 날짜를 기본값으로 사용
            if not from_date:
                from_date = datetime.date.today().strftime("%Y-%m-%d")
            if not to_date:
                to_date = datetime.date.today().strftime("%Y-%m-%d")

            # 출석 내역 URL 설정
            attendance_url = (
                self.client.determine_server_url(self.user_info["user_id"])
                + "rb_attend_record.php"
            )

            # 요청 데이터 준비
            request_data = {
                "from_date": from_date,
                "to_date": to_date,
            }

            # 암호화 및 요청
            encrypted_data = self.client.sencrypt(json.dumps(request_data))
            params = {"key": encrypted_data}

            # POST 요청 보내기
            response = self.client.session.post(attendance_url, data=params)

            # 응답 확인
            if response.status_code == 200:
                result = self.client.sdecrypt(response.text)
                result_json = json.loads(result)

                if "result" in result_json and "record" in result_json["result"]:
                    return result_json["result"]["record"]
                else:
                    logger.warning("출석 내역이 없거나 응답 형식이 올바르지 않습니다")
                    return []
            else:
                raise AttendanceError(
                    f"출석 내역 조회 실패: HTTP 상태 코드 {response.status_code}"
                )

        except Exception as e:
            if isinstance(e, (NotLoggedInError, InvalidArgumentError)):
                raise
            else:
                logger.exception("출석 내역 조회 중 예외 발생")
                raise AttendanceError(f"출석 내역 조회 중 예외 발생: {str(e)}")

    def get_notices(self, page: int = 1, count: int = 10) -> List[Dict[str, Any]]:
        """
        공지사항 목록 조회

        Args:
            page: 조회할 페이지 번호 (1부터 시작)
            count: 한 페이지당 가져올 항목 수

        Returns:
            공지사항 목록

        Raises:
            NotLoggedInError: 로그인되지 않은 경우
            InvalidArgumentError: 인자가 유효하지 않은 경우
            AttendanceError: 공지사항 조회 실패 시
        """
        if not self.is_logged_in:
            raise NotLoggedInError("공지사항을 조회하려면 먼저 로그인하세요")

        if page < 1:
            raise InvalidArgumentError("page는 1 이상이어야 합니다")
        if count < 1:
            raise InvalidArgumentError("count는 1 이상이어야 합니다")

        try:
            # 공지사항 URL 설정
            notice_url = (
                self.client.determine_server_url(self.user_info["user_id"])
                + "rb_notice.php"
            )

            # 요청 데이터 준비
            request_data = {
                "page": page,
                "count": count,
            }

            # 암호화 및 요청
            encrypted_data = self.client.sencrypt(json.dumps(request_data))
            params = {"key": encrypted_data}

            # POST 요청 보내기
            response = self.client.session.post(notice_url, data=params)

            # 응답 확인
            if response.status_code == 200:
                result = self.client.sdecrypt(response.text)
                result_json = json.loads(result)

                if "result" in result_json and "notice" in result_json["result"]:
                    return result_json["result"]["notice"]
                else:
                    logger.warning("공지사항이 없거나 응답 형식이 올바르지 않습니다")
                    return []
            else:
                raise AttendanceError(
                    f"공지사항 조회 실패: HTTP 상태 코드 {response.status_code}"
                )

        except Exception as e:
            if isinstance(e, (NotLoggedInError, InvalidArgumentError)):
                raise
            else:
                logger.exception("공지사항 조회 중 예외 발생")
                raise AttendanceError(f"공지사항 조회 중 예외 발생: {str(e)}")

    def get_attendance_statistics(self) -> Dict[str, Any]:
        """
        출석 통계 조회

        Returns:
            출석 통계 정보

        Raises:
            NotLoggedInError: 로그인되지 않은 경우
            AttendanceError: 출석 통계 조회 실패 시
        """
        if not self.is_logged_in:
            raise NotLoggedInError("출석 통계를 조회하려면 먼저 로그인하세요")

        try:
            # 출석 통계 URL 설정
            stats_url = (
                self.client.determine_server_url(self.user_info["user_id"])
                + "rb_attend_status.php"
            )

            # 요청 데이터 준비
            request_data = {}

            # 암호화 및 요청
            encrypted_data = self.client.sencrypt(json.dumps(request_data))
            params = {"key": encrypted_data}

            # POST 요청 보내기
            response = self.client.session.post(stats_url, data=params)

            # 응답 확인
            if response.status_code == 200:
                result = self.client.sdecrypt(response.text)
                result_json = json.loads(result)

                if "result" in result_json and "status" in result_json["result"]:
                    return result_json["result"]["status"]
                else:
                    logger.warning("출석 통계가 없거나 응답 형식이 올바르지 않습니다")
                    return {}
            else:
                raise AttendanceError(
                    f"출석 통계 조회 실패: HTTP 상태 코드 {response.status_code}"
                )

        except Exception as e:
            if isinstance(e, NotLoggedInError):
                raise
            else:
                logger.exception("출석 통계 조회 중 예외 발생")
                raise AttendanceError(f"출석 통계 조회 중 예외 발생: {str(e)}")

    def search_user_by_id(self, student_id: str) -> List[Dict[str, Any]]:
        """
        학번으로 사용자 검색

        Args:
            student_id: 검색할 학번

        Returns:
            검색된 사용자 목록

        Raises:
            NotLoggedInError: 로그인되지 않은 경우
            InvalidArgumentError: 학번이 유효하지 않은 경우
            AttendanceError: 사용자 검색 실패 시
        """
        if not self.is_logged_in:
            raise NotLoggedInError("사용자를 검색하려면 먼저 로그인하세요")

        if not student_id or not isinstance(student_id, str):
            raise InvalidArgumentError("유효한 학번을 입력하세요")

        try:
            # 사용자 검색 실행
            results = self.client.search_user_by_id(student_id)
            return results

        except Exception as e:
            if isinstance(e, (NotLoggedInError, InvalidArgumentError)):
                raise
            else:
                logger.exception("사용자 검색 중 예외 발생")
                raise AttendanceError(f"사용자 검색 중 예외 발생: {str(e)}")

    def search_user_by_name(self, student_name: str) -> List[Dict[str, Any]]:
        """
        이름으로 사용자 검색

        Args:
            student_name: 검색할 이름

        Returns:
            검색된 사용자 목록

        Raises:
            NotLoggedInError: 로그인되지 않은 경우
            InvalidArgumentError: 이름이 유효하지 않은 경우
            AttendanceError: 사용자 검색 실패 시
        """
        if not self.is_logged_in:
            raise NotLoggedInError("사용자를 검색하려면 먼저 로그인하세요")

        if not student_name or not isinstance(student_name, str):
            raise InvalidArgumentError("유효한 이름을 입력하세요")

        try:
            # 사용자 검색 실행
            results = self.client.search_user_by_name(student_name)
            return results

        except Exception as e:
            if isinstance(e, (NotLoggedInError, InvalidArgumentError)):
                raise
            else:
                logger.exception("사용자 검색 중 예외 발생")
                raise AttendanceError(f"사용자 검색 중 예외 발생: {str(e)}")

    # 기존 서명 유지를 위한 메소드
    def search_user(
        self, search_term: str, search_by_name: bool = False
    ) -> List[Dict[str, Any]]:
        """
        사용자 검색 (기존 코드 호환성 유지용)

        Args:
            search_term: 검색어 (학번 또는 이름)
            search_by_name: True일 경우 이름으로 검색, False일 경우 학번으로 검색

        Returns:
            검색된 사용자 목록
        """
        if search_by_name:
            return self.search_user_by_name(search_term)
        else:
            return self.search_user_by_id(search_term)

    def send_friend_request(self, user_info_num: Union[str, int]) -> bool:
        """
        친구 요청 보내기

        Args:
            user_info_num: 사용자 정보 번호 (문자열 또는 정수)

        Returns:
            친구 요청 성공 여부

        Raises:
            NotLoggedInError: 로그인되지 않은 경우
            InvalidArgumentError: 사용자 정보 번호가 유효하지 않은 경우
            AttendanceError: 친구 요청 실패 시
        """
        if not self.is_logged_in:
            raise NotLoggedInError("친구 요청을 보내려면 먼저 로그인하세요")

        # 정수형인 경우 문자열로 변환
        if isinstance(user_info_num, int):
            user_info_num = str(user_info_num)

        if not user_info_num or not isinstance(user_info_num, str):
            raise InvalidArgumentError("유효한 사용자 정보 번호를 입력하세요")

        try:
            # 친구 요청 보내기
            result = self.client.send_friend_request(user_info_num)
            return result

        except Exception as e:
            if isinstance(e, (NotLoggedInError, InvalidArgumentError)):
                raise
            else:
                logger.exception("친구 요청 보내기 중 예외 발생")
                raise AttendanceError(f"친구 요청 보내기 중 예외 발생: {str(e)}")

    def get_profile_image_url(self, student_id: str) -> str:
        """
        학생 프로필 사진 URL 가져오기

        Args:
            student_id: 학번

        Returns:
            프로필 사진 URL

        Raises:
            InvalidArgumentError: 학번이 유효하지 않은 경우
        """
        if not student_id or not isinstance(student_id, str):
            raise InvalidArgumentError("유효한 학번을 입력하세요")

        return (
            f"https://push.kyonggi.ac.kr:80/xidps/de_p_kgu_image?user_id={student_id}"
        )
