from setuptools import setup, find_packages

setup(
    name="generative",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "anthropic>=0.2.9",
        "google-generativeai>=0.1.0",
        "openai>=0.27.7",
        "protobuf",
        "python-dotenv>=1.0.0",
        "RestrictedPython>=6.0",
        "urllib3<2.0",
    ],
    extras_require={
        "dev": [
            "black>=3.3.0",
            "flake8>=6.0.0",
            "mypy>=1.3.0",
            "pre-commit>=3.3.2",
            "pytest>=7.3.1",
            "pytest-mock>=3.10.0",
            "redis>=4.5.5",
            "tox>=4.5.2",
        ]
    },
    package_data={"generative": ["py.typed"]},
)
