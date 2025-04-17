#!/usr/bin/env python
"""
도서관 모듈 테스트를 실행하는 스크립트
"""
import os
import sys
import unittest

# 모듈 경로 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


def run_library_tests():
    """도서관 모듈 테스트 실행"""
    # 테스트 디렉토리 경로
    test_dir = os.path.dirname(os.path.abspath(__file__))

    # 테스트 스위트 로드
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 도서관 모듈 테스트 파일들 추가
    suite.addTests(loader.discover(test_dir, pattern="test_library_*.py"))

    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 결과 반환
    return result.wasSuccessful()


if __name__ == "__main__":
    # 테스트 실행 및 종료 코드 반환
    success = run_library_tests()
    sys.exit(0 if success else 1)
