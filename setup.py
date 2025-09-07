from setuptools import setup, find_packages

setup(
    name="xml_analyzer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "lxml",
        "tqdm",
        "ttkthemes>=3.2.0",
        "Pillow",  # for image handling
    ],
    python_requires=">=3.7",
)