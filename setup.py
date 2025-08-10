from setuptools import setup, find_packages

setup(
    name='ieditllm',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'boto3',
    ],
    entry_points={
        'console_scripts': [
            'ieditllm = iedit.main:cli',
        ],
    },
)