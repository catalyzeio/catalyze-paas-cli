from setuptools import setup, find_packages

import catalyze.config

with open("requirements.txt", 'r') as file:
    setup(
        name="catalyze",
        version=catalyze.config.version,
        description="CLI for Catalyze Platform-as-a-Service interaction",
        author="Catalyze",
        author_email="support@catalyze.io",
        packages=find_packages(),
        install_requires=file.readlines(),
        include_package_data=True,
        url="https://github.com/catalyzeio/catalyze-paas-cli",
        entry_points={
            "console_scripts": ["catalyze = catalyze:run"]
        }
    )
