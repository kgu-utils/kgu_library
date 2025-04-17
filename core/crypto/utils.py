"""
암호화 관련 유틸리티 함수
"""


def hex_comma_str_to_bytes(hex_comma_str: str) -> bytes:
    """
    쉼표로 구분된 16진수 문자열을 바이트 배열로 변환합니다.

    Args:
        hex_comma_str: 쉼표로 구분된 16진수 문자열 (예: "80,E3,4F,8F")

    Returns:
        변환된 바이트 배열
    """
    # 쉼표로 구분하고 공백 제거
    hex_values = [x.strip() for x in hex_comma_str.split(",")]

    # 16진수 문자열을 정수로 변환 후 바이트로 변환
    return bytes([int(x, 16) for x in hex_values])


def bytes_to_hex_comma_str(byte_data: bytes) -> str:
    """
    바이트 배열을 쉼표로 구분된 16진수 문자열로 변환합니다.

    Args:
        byte_data: 바이트 배열

    Returns:
        쉼표로 구분된 16진수 문자열 (예: "80,E3,4F,8F")
    """
    return ",".join([f"{b:02X}" for b in byte_data])


def create_seed_cipher(key_str: str, iv_str: str):
    """
    SEED CBC 암호화 객체를 생성합니다.

    Args:
        key_str: 쉼표로 구분된 16진수 키 문자열
        iv_str: 쉼표로 구분된 16진수 IV 문자열

    Returns:
        SeedCbcCipher 객체
    """
    from kgu_library.KISA_SEED_128_CBC.seed import SeedCbcCipher

    key = hex_comma_str_to_bytes(key_str)
    iv = hex_comma_str_to_bytes(iv_str)

    return SeedCbcCipher(key=key, iv=iv)
