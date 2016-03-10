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
        'psutil>=3.0.0',
    ],
    entry_points='''
        [console_scripts]
        tunneler=tunneler.main:cli
    ''',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: System :: Networking',
    ],
)
