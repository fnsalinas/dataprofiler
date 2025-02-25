
from setuptools import setup, find_packages

setup(
    name='dataprofiler',
    version='1.0',
    description='Data Profiler',
    author='Fabio Salinas',
    author_email='fabio.salinas1982@gmail.com',
    license='MIT',
    packages=find_packages(where='src'),
    package_dir={'':'src'},
    zip_safe=False,
    url="https://github.com/fnsalinas/dataprofiler",
    python_requires='>=3.10'
)
