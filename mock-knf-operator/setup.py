import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="prometheus-mock-knf-charm",
    version="0.0.1",
    author="David García",
    author_email="david.garcia@canonical.com",
    description="Kubernetes Charm/Operator for Prometheus",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/davigar15/prometheus-mock-knf-charm",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)
