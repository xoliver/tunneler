from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='tunneler',
    version='0.5.1',
    packages=['tunneler'],
    author='Xavier Oliver',
    author_email='xoliver@gmail.com',
    url='http://github.com/xoliver/tunneler/',
    description='Tunnel manager',
    long_description=readme(),
    install_requires=[
        'click',
        'colorama',
        'psutil',
    ],
    entry_points='''
        [console_scripts]
        tunneler=tunneler.main:cli
    ''',
)
