from setuptools import setup, find_packages
import os

# Read version
version = {}
with open(os.path.join("tamper_framework", "__version__.py")) as f:
    exec(f.read(), version)

# Read README
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="sqlmap-tamper-framework",
    version=version["__version__"],
    author=version["__author__"],
    author_email="support@rothackers.com",
    description=version["__description__"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/noobforanonymous/sqlmap-tamper-collection",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies - pure Python
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
