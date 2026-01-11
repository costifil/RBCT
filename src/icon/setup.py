import setuptools

setuptools.setup(
    name="icon",
    version="0.0.1",
    author="CF",
    author_email='',
    description="Icon module",
    long_description="",
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
    install_requires=[],
    entry_points = {
        'console_scripts': ['icon=icon.icon:main']
    },
    include_package_data=False
)
