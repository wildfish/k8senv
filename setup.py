from setuptools import setup
import os


def load_requirements():
    with open(os.path.join(os.path.dirname(__file__), "requirements-pkg.in")) as f:
        return f.readlines()


setup(
    name='k8senv',
    version='0.0.0',
    packages=['k8senv'],
    url='',
    license='BSD',
    author='Wildfish',
    author_email='developers@wildfish.com',
    description='Manages access to multiple kubernetes environments',
    install_requires=load_requirements(),
    entry_points={
        'console_scripts': [
            'k8senv = k8senv:cli',
        ],
    },
)
