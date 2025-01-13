from setuptools import setup, find_packages

setup(
    name="bus_ca_simulation",
    version="0.1.0",
    description="Cellular automata based bus network simulation",
    author='Diego Ramos',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "bus_ca_simulation":["data/**/*.json"]
    },
    install_requires=[
        'matplotlib',
        'numpy',
        'pandas',
        'networkx'
    ]
)