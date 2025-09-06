from setuptools import setup, find_packages

setup(
    name="xml_analyzer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "lxml",  # for faster XML processing
        "tqdm",  # for progress bars
    ],
    author="Your Name",
    description="XML Analysis and Database Storage Tool",
    python_requires=">=3.7",
)