from setuptools import setup
from rf2settings.globals import get_version


setup(
    name='rf2settings',
    version=get_version(),
    packages=['rf2settings'],
    install_requires=[
        'appdirs',
    ],
    url='https://github.com/tappi287/rf2_video_settings/',
    license='MIT',
    author='Stefan Tapper',
    author_email='tapper.stefan@gmail.com',
    description='Alter rFactor 2 settings'
)
