from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='ieditllm',
    version='0.1.0',
    author='Giovanni Zappella',
    author_email='giovanni.zappella@example.com',
    description='CLI tools to improve LaTeX documents using LLMs',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/giovannizappella/ieditllm',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'boto3',
        'google-generativeai',
        'toml',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    entry_points={
        'console_scripts': [
            'ieditllm = iedit.main:cli',
        ],
    },
)
