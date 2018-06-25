from setuptools import setup

setup(
    name='simulator',
    version='1.0',
    scripts=['simulator'],
    install_requires=['python-dateutil'],
    author="Shashank Singh",
    author_email="shashank#bankoncube.com",
    description="A small example package",
    url='http://github.com/CubeConsumerServivesPvtLtd/simulator',
    license='MIT',
    packages=['simulator'],
    zip_safe=False
)

