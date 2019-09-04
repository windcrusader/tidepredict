import pathlib
import setuptools

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setuptools.setup(
    name="psatools",
    version="0.0.1",
    description="Provides wrappers for electrical engineering calculations",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/windcrusader/psatools",
    author="Brad Henderson",
    author_email="ba.henderson@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    install_requires=["numpy"],
)