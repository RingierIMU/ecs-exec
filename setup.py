from setuptools import setup, find_packages
from distutils.util import convert_path

with open("README.md", "r") as fh:
    long_description = fh.read()

main_ns = {}
ver_path = convert_path("ecs_exec/version.py")
with open(ver_path) as ver_file:
    exec(ver_file.read(), main_ns)

setup(
    name="ecs-exec",
    version=main_ns["__version__"],
    author="Ringier Tech",
    author_email="tools@ringier.co.za",
    description="Simple script to allow one to execute commands on AWS ECS Fargate once ECS exec has been correctly configured.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RingierIMU/ecs-exec",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3",
    install_requires=[
        "boto3",
        "argparse",
    ],
    entry_points={
        "console_scripts": [
            "ecs-exec=ecs_exec.__main__:main",
        ],
    },
)
