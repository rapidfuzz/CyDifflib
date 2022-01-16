from skbuild import setup

with open('README.md', 'rt', encoding="utf8") as f:
    readme = f.read()

setup(
    name="cydifflib",
    version="1.0.0",
    url="https://github.com/maxbachmann/cydifflib",
    author="Max Bachmann",
    author_email="pypi@maxbachmann.de",
    description="Fast implementation of difflib's algorithms",
    long_description=readme,
    long_description_content_type="text/markdown",

    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License"
    ],

    packages=["cydifflib"],
    package_dir={'':'src'},
    zip_safe=True,
    include_package_data=True,
    python_requires=">=3.6",
)
