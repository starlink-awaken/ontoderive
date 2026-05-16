from setuptools import setup, find_packages

setup(
    name="ontoderive",
    version="1.2.0",
    description="OntoDerive - Fact-driven Knowledge Engineering & Derivation Framework",
    author="夏明星",
    author_email="",
    packages=find_packages(),
    py_modules=["engine.derive"],
    python_requires=">=3.8",
    install_requires=[],
    entry_points={
        "console_scripts": [
            "ontoderive=engine.derive:main",
        ],
    },
)
