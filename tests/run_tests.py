#!/usr/bin/env python
"""
모든 테스트를 실행하는 스크립트
"""
import unittest
import sys
import os
import argparse

# 모듈 경로 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from kgu_library.tests.run_e2e_tests import run_unittest_e2e_tests, run_pytest_e2e_tests


def run_unit_tests():
    """단위 테스트만 실행하는 함수"""
    # 테스트 디렉토리 경로
    test_dir = os.path.dirname(os.path.abspath(__file__))

    # 테스트 모듈 발견 및 테스트 스위트 로드
    loader = unittest.TestLoader()

    # e2e 테스트 제외하고 단위 테스트만 포함
    suite = unittest.TestSuite()
    unit_tests = loader.discover(test_dir, pattern="test_*.py")

    # e2e 테스트 디렉토리 경로
    e2e_dir = os.path.join(test_dir, "e2e")

    # 모든 테스트 중에서 e2e 테스트 디렉토리에 있지 않은 테스트만 필터링
    for test in unit_tests:
        if isinstance(test, unittest.TestSuite):
            for test_case in test:
                # 테스트 모듈 파일 경로 확인
                test_module = test_case.__module__
                if "e2e" not in test_module:
                    suite.addTest(test_case)

    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 결과 반환
    return result.wasSuccessful()


def run_all_tests(include_e2e=True):
    """모든 테스트를 실행하는 함수"""
    print("=== 단위 테스트 실행 ===")
    unit_test_success = run_unit_tests()

    e2e_test_success = True
    if include_e2e:
        print("\n=== E2E 테스트 실행 ===")
        e2e_unittest_result = run_unittest_e2e_tests()
        e2e_pytest_result = run_pytest_e2e_tests()
        e2e_test_success = e2e_unittest_result == 0 and e2e_pytest_result == 0

    return unit_test_success and e2e_test_success


def parse_args():
    """명령줄 인자 파싱"""
    parser = argparse.ArgumentParser(description="kgu_library 테스트 실행")

    parser.add_argument(
        "--unit-only", action="store_true", help="단위 테스트만 실행 (e2e 테스트 제외)"
    )

    parser.add_argument(
        "--e2e-only", action="store_true", help="e2e 테스트만 실행 (단위 테스트 제외)"
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.unit_only:
        print("단위 테스트만 실행")
        success = run_unit_tests()
    elif args.e2e_only:
        print("e2e 테스트만 실행")
        # e2e_tests 모듈의 메인 함수 호출
        from kgu_library.tests.run_e2e_tests import main as run_e2e_main

        sys.exit(run_e2e_main())
    else:
        print("모든 테스트 실행")
        success = run_all_tests()

    sys.exit(0 if success else 1)
