import setuptools
from setuptools import setup

setup(
    name='extract_data_from_blockchain',
    version='1.0',
    packages=setuptools.find_packages(),
    url='',
    license='',
    author='cesar.paz',
    author_email='Cesar Paz',
    description='Program done to learn about web3 development',
    entry_points={
        'console_scripts': [
            'extract_data=extract_data.main_program.mainApp:main'
        ],
    }
)
