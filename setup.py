"""
UpdateData2Sql 项目安装配置
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取 README 文件
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# 读取 requirements.txt
with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="updatedata2sql",
    version="1.0.0",
    author="Euclid_Jie",
    author_email="your.email@example.com",
    description="从多个数据源获取指数数据并更新到数据库的Python项目",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/UpdateData2Sql",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Database",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "update-index=src.scripts.index_updater:main",
            "update-fund=src.scripts.fund_updater:main",
            "update-company=src.scripts.company_updater:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md", "*.yml", "*.yaml"],
    },
    keywords="finance, data, database, index, fund, akshare, wind",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/UpdateData2Sql/issues",
        "Source": "https://github.com/yourusername/UpdateData2Sql",
        "Documentation": "https://github.com/yourusername/UpdateData2Sql/docs",
    },
)
