import pathlib
import setuptools

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setuptools.setup(
    name="tidepredict",
    version="0.0.1",
    description="Tide Prediction tools",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/windcrusader/tidepredict",
    author="Brad Henderson",
    author_email="ba.henderson@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=2.7",
    install_requires=["numpy","matplotlib","pandas","jinja2","scipy"],
)