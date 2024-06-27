from setuptools import find_namespace_packages, setup

with open("README.md") as fh:
    LONG_DESC = fh.read()
    setup(
        name="hydra-paired-sweeper",
        version="1.0.0",
        author="B12 Consulting",
        description="Hydra sweeper allowing one to iterate multiple parameters in parallel.",
        long_description=LONG_DESC,
        long_description_content_type="text/markdown",
        url="www.b12-consulting.com",
        packages=find_namespace_packagas(include=["hydra_plugins.*"]),
        classifiers=[
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Operating System :: OS Independent",
        ],
        install_requires=[
            "hydra-core",
        ],
        # If this plugin is providing configuration files, be sure to include them in the package.
        # See MANIFEST.in.
        # For configurations to be discoverable at runtime, they should also be added to the search path.
        include_package_data=True,
    )
