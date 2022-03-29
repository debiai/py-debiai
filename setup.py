import setuptools

setuptools.setup(
    name="debiai",
    version="0.15.1",
    author="IRT-SystemX",
    author_email="debiai@irt-systemx.fr",
    description="DebiAI python module",
    license="Apache 2.0",
    keywords="DebiAI, Data vis, AI, Bias",
    url="https://github.com/debiai/py-debiai",

    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'numpy',
        'pandas',
        'requests'
    ]
)
