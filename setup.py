from setuptools import setup, find_packages

setup(
    name="apk_quim_plant",
    version="1.0.0",
    author="Carl",
    description="Analise Fitoquimica de Plantas",
    packages=find_packages(include=['complant', 'complant.*']),
    install_requires=[
        "requests>=2.31.0",
    ],
    python_requires=">=3.8",
)
