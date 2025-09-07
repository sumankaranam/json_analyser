from setuptools import setup, find_packages

setup(
    name="xml_analyzer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.3.0",
        "lxml>=4.9.0",
        "tqdm>=4.65.0",
        "ttkthemes>=3.2.0",
        "Pillow>=9.0.0",  # for image handling
        "python-tk",      # for GUI
        "sqlalchemy>=1.4.0",  # for database operations
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=22.0.0',
            'flake8>=4.0.0',
        ]
    },
    python_requires=">=3.7",
    author="Your Name",
    description="XML Duplicate File Analyzer with GUI",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Desktop Environment :: File Managers",
    ],
)