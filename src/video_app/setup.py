import setuptools
from video_app import version

setuptools.setup(
    name="Video Projection",
    version=version.__version__,
    author="CF",
    author_email="",
    description="video projection module",
    long_description="This module will play some apps on the desired screen",
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
        'gui_scripts': ['video_projection=video_app.video_app:main']
    },
    include_package_data=True
)