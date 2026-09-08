from setuptools import setup, find_packages

setup(
    name="macs-multi-agent-compliance-system",
    version="0.1.0",
    description="Multi-Agent Compliance Monitoring System for Financial Regulatory Compliance",
    author="Zetheta Intern",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "langchain>=0.2.0",
        "langgraph>=0.1.0",
        "openai>=1.30.0",
        "anthropic>=0.25.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "httpx>=0.27.0",
        "tenacity>=8.2.0",
        "rich>=13.0.0",
        "vaderSentiment>=3.3.2",
        "textblob>=0.18.0",
        "beautifulsoup4>=4.12.0",
        "cryptography>=42.0.0",
        "tiktoken>=0.7.0",
        "numpy>=1.24.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
        ],
    },
)
