from setuptools import find_packages
from setuptools import setup


def find_required() -> list[str]:
    with open("requirements.txt") as f:
        return f.read().splitlines()


def find_dev_required() -> list[str]:
    with open("requirements-dev.txt") as f:
        return f.read().splitlines()


def get_version(filename='vedro_jira_failed_reporter/version') -> str:
    return open(filename, "r").read().strip()


setup(
    name="vedro-jira-failed-reporter",
    version=get_version(),
    description="vedro.io plugin for reporting about flaky tests into jira "
                "(with plugin enabled in flaky check runs)",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Yuriy Sagitov",
    author_email="pro100.ko10ok@gmail.com",
    python_requires=">=3.7",
    url="https://github.com/ko10ok/vedro-jira-failed-reporter",
    license="Apache-2.0",
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=find_required(),
    tests_require=find_dev_required(),
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
    ],
    package_data={
        'vedro_jira_failed_reporter': ['version', 'py.typed'],
    },
)
