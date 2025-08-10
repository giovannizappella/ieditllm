# Developer Guide

This guide provides instructions for developers on how to build and publish the `ieditllm` package to PyPI.

## Publishing to PyPI

To publish a new version of `ieditllm` to PyPI, follow these steps:

1.  **Navigate to the project directory:**

    ```bash
    cd /path/to/your/ieditllm
    ```

2.  **Create and activate a virtual environment (if you haven't already):**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install build and upload dependencies:**

    ```bash
    pip install wheel twine
    ```

4.  **Build the distribution packages:**

    ```bash
    python setup.py sdist bdist_wheel
    ```

    This will create `tar.gz` and `.whl` files in the `dist/` directory.

5.  **Upload the packages to PyPI:**

    ```bash
    twine upload dist/*
    ```

    You will be prompted for your PyPI username and password (or API token). Enter them when requested.
