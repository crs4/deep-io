import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="deep-io",
    version="0.1.1",
    author="Jose F. Saenz-Cogollo",
    author_email="jsaenz@crs4.it",
    description="Python library for accessing the DEEP Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    install_requires=[
        "hyperpeer-py"
    ],
    extras_require={
        "all": []
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL-3.0 License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X"
    ],
    python_requires=">=3.7",
)