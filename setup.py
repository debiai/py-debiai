import setuptools

setuptools.setup(
    name="debiai",
    version="0.15.0",
    author="IRT-SystemX",
    author_email="debiai@irt-systemx.fr",
    description="DebiAI python module",
    long_description="""# Debiai (Python package)
Package for debiai usage.

## Usage
```from debiai import debiai``` is the only import needed.

## Contents
* `debiai` should be used to communicate data with the debiai backend.

_Property of IRT-SystemX_
""",
    long_description_content_type="text/markdown",
    url="https://github.com/DebiAI/py-debiai",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Apache 2.0",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'numpy',
        'pandas',
        'requests'
    ]
)
