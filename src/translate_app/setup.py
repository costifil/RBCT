import setuptools
from translate_app import version

setuptools.setup(
    name="Translate Subtitle",
    version=version.__version__,
    author="CF",
    author_email="",
    description="Subtitle translation",
    long_description="This module will get translation and printed as subtitle on OBS",
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: CF License",
        "Operating System :: Windows OS",
    ],
    python_requires='>=3.9',
    install_requires=[],
    entry_points = {
        'console_scripts': ['translate=translate_app.translate:main']
    },
    include_package_data=True
)