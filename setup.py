from setuptools import setup, find_packages

setup(
    name="kgu_library",
    version="0.1.0",
    description="경기대학교 관련 API 라이브러리 모음",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="rmagur1203",
    author_email="rmagur1203@kyonggi.ac.kr",
    url="https://github.com/kgu-utils/kgu_library",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "urllib3>=1.26.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
    project_urls={
        "Bug Reports": "https://github.com/kgu-utils/kgu_library/issues",
        "Source": "https://github.com/kgu-utils/kgu_library",
    },
)
