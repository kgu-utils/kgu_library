"""
암호화 관련 유틸리티 함수 테스트
"""

import unittest
from kgu_library.core.crypto import (
    hex_comma_str_to_bytes,
    bytes_to_hex_comma_str,
    create_seed_cipher,
    SeedCbcCipher,
)


class TestCrypto(unittest.TestCase):
    """암호화 유틸리티 테스트 클래스"""

    def test_hex_comma_str_to_bytes(self):
        """hex_comma_str_to_bytes 함수 테스트"""
        # 테스트 케이스
        hex_str = "80,E3,4F,8F,08,10"
        expected = bytes([0x80, 0xE3, 0x4F, 0x8F, 0x08, 0x10])

        # 함수 실행
        result = hex_comma_str_to_bytes(hex_str)

        # 결과 검증
        self.assertEqual(result, expected)

    def test_bytes_to_hex_comma_str(self):
        """bytes_to_hex_comma_str 함수 테스트"""
        # 테스트 케이스
        byte_data = bytes([0x80, 0xE3, 0x4F, 0x8F, 0x08, 0x10])
        expected = "80,E3,4F,8F,08,10"

        # 함수 실행
        result = bytes_to_hex_comma_str(byte_data)

        # 결과 검증
        self.assertEqual(result, expected)

    def test_hex_conversion_roundtrip(self):
        """hex 변환 왕복 테스트"""
        # 테스트 케이스
        original = "80,E3,4F,8F,08,10,70,F1,E9,F3,94,37,0A,D4,05,89"

        # 왕복 변환
        byte_data = hex_comma_str_to_bytes(original)
        result = bytes_to_hex_comma_str(byte_data)

        # 결과 검증
        self.assertEqual(result, original)

    def test_create_seed_cipher(self):
        """create_seed_cipher 함수 테스트"""
        # 테스트 키와 IV
        key_str = "80,E3,4F,8F,08,10,70,F1,E9,F3,94,37,0A,D4,05,89"
        iv_str = "20,8D,66,A7,30,A8,1A,81,6F,BA,D9,FA,36,10,25,01"

        # 함수 실행
        cipher = create_seed_cipher(key_str, iv_str)

        # 결과 검증
        self.assertIsInstance(cipher, SeedCbcCipher)

    def test_seed_cipher_encrypt_decrypt_roundtrip(self):
        """SEED 암호화/복호화 왕복 테스트"""
        # 테스트 키와 IV
        key_str = "80,E3,4F,8F,08,10,70,F1,E9,F3,94,37,0A,D4,05,89"
        iv_str = "20,8D,66,A7,30,A8,1A,81,6F,BA,D9,FA,36,10,25,01"

        # 테스트 데이터
        plaintext = "안녕하세요, 이것은 테스트 데이터입니다."

        # SeedCbcCipher 객체 생성
        cipher = create_seed_cipher(key_str, iv_str)

        # 암호화 및 복호화
        encrypted = cipher.encrypt(plaintext.encode("utf-8"))
        decrypted = cipher.decrypt(encrypted)

        # 결과 검증
        self.assertEqual(decrypted.decode("utf-8"), plaintext)


if __name__ == "__main__":
    unittest.main()
