import setuptools

setuptools.setup(
    name="instapull",
    version="0.9",
    packages=setuptools.find_packages(),
    entry_points={"console_scripts": ["instapull=instapull.__main__:main"]},
    author="Frode Hus",
    author_email="frode.hus@outlook.com",
    description="Simple tool that lets you dump Instagram posts by user or hashtag",
    url="https://www.frodehus.com",
    python_requires=">=3.6",
    install_requires=["requests", "argparse"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
