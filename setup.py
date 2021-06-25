import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ecs-exec",
    version="0.0.3",
    author="Ringier Tech",
    author_email="tools@ringier.co.za",
    description="Simple script to allow one to execute commands on AWS ECS Fargate once ECS exec has been correctly configured.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RingierIMU/ecs-exec",
    packages=setuptools.find_packages(),
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
