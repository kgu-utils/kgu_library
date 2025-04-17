#!/usr/bin/env python
"""
e2e 테스트 실행 스크립트

이 스크립트는 kgu_library의 end-to-end 테스트를 실행합니다.
"""
import os
import sys
import argparse
import unittest
import pytest
from dotenv import load_dotenv

# 모듈 경로 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# 환경 변수 로드
load_dotenv()


def run_unittest_e2e_tests():
    """unittest 기반 e2e 테스트 실행"""
    test_dir = os.path.join(os.path.dirname(__file__), "e2e")
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(test_dir, pattern="test_*.py")

    # 결과 스트림을 표준 출력으로 설정
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)

    return 0 if result.wasSuccessful() else 1


def run_pytest_e2e_tests():
    """pytest 기반 e2e 테스트 실행"""
    test_dir = os.path.join(os.path.dirname(__file__), "e2e")
    result = pytest.main(["-xvs", test_dir])

    return 0 if result == 0 else 1


def run_specific_test(test_name):
    """특정 테스트만 실행"""
    test_dir = os.path.join(os.path.dirname(__file__), "e2e")
    result = pytest.main(["-xvs", os.path.join(test_dir, f"test_{test_name}.py")])

    return 0 if result == 0 else 1


def parse_args():
    """명령줄 인자 파싱"""
    parser = argparse.ArgumentParser(description="kgu_library e2e 테스트 실행")

    test_type_group = parser.add_mutually_exclusive_group()
    test_type_group.add_argument(
        "--unittest", action="store_true", help="unittest 기반 테스트만 실행"
    )
    test_type_group.add_argument(
        "--pytest", action="store_true", help="pytest 기반 테스트만 실행"
    )

    parser.add_argument(
        "--test", type=str, help="실행할 특정 테스트 이름 (예: library_api_flow)"
    )

    return parser.parse_args()


def main():
    """메인 함수"""
    args = parse_args()

    if args.test:
        print(f"특정 테스트 실행: {args.test}")
        return run_specific_test(args.test)

    if args.unittest:
        print("unittest 기반 e2e 테스트 실행")
        return run_unittest_e2e_tests()

    if args.pytest:
        print("pytest 기반 e2e 테스트 실행")
        return run_pytest_e2e_tests()

    # 기본적으로 모든 테스트 실행
    print("모든 e2e 테스트 실행")
    unittest_result = run_unittest_e2e_tests()
    pytest_result = run_pytest_e2e_tests()

    return 1 if (unittest_result != 0 or pytest_result != 0) else 0


if __name__ == "__main__":
    sys.exit(main())
