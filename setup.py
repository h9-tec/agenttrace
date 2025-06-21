from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="agenttrace",
    version="0.1.0",
    author="Hesham Haroon",
    author_email="heshamharoon19@gmail.com",
    description="Lightweight observability for AI agents - trace and visualize LangChain, CrewAI, and custom AI agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/h9-tec/agenttrace",
    project_urls={
        "Bug Tracker": "https://github.com/h9-tec/agenttrace/issues",
        "Documentation": "https://github.com/h9-tec/agenttrace",
        "Source Code": "https://github.com/h9-tec/agenttrace",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*", "docs", "docs.*"]),
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn[standard]>=0.15.0",
        "pydantic>=1.8.0",
        "python-multipart>=0.0.5",
    ],
    extras_require={
        "crewai": ["crewai>=0.1.0"],
        "langchain": ["langchain>=0.0.200"],
        "openrouter": ["langchain-openai>=0.0.5", "python-dotenv>=0.19.0"],
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.910",
            "isort>=5.9",
        ],
        "all": ["crewai>=0.1.0", "langchain>=0.0.200", "langchain-openai>=0.0.5", "python-dotenv>=0.19.0"],
    },
    entry_points={
        "console_scripts": [
            "agenttrace=agenttrace.__main__:main",
        ],
    },
    include_package_data=True,
    package_data={
        "agenttrace": ["viewer/templates/*.html", "viewer/static/**/*"],
    },
) 