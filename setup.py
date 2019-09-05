import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="python_license_linter",
    version="0.0.1",
    author="Zjan Turla",
    author_email="zjancarlo@gmail.com",
    description="Gets license information of packages listed in provided requirements.txt and checks them against a list of blacklisted licenses.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zjancarlo/python-license-linter",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7',
    entry_points={
        'console_scripts': [
            'lint_python_licenses = python_license_linter.lint_python_licenses:main'
        ]
    }
)