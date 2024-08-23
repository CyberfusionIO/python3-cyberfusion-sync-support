"""A setuptools based setup module."""

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="python3-cyberfusion-sync-support",
    version="1.2.7.4",
    description="Library for syncing objects (e.g. directories).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Cyberfusion",
    author_email="support@cyberfusion.io",
    url="https://github.com/CyberfusionIO/python3-cyberfusion-sync-support",
    platforms=["linux"],
    packages=[
        "cyberfusion.SyncSupport",
    ],
    package_dir={"": "src"},
    data_files=[],
    install_requires=[
        "cached_property==1.5.2",
        "python3-cyberfusion-common~=2.9",
        "python3-cyberfusion-cluster-support~=1.0",
    ],
)
