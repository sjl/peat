import setuptools

VERSION = '1.0.0'

setuptools.setup(
    name='peat',
    version=VERSION,
    description='Repeat commands!',
    url='https://github.com/bmcorser/peat',
    py_modules=['peat'],
    entry_points='''
        [console_scripts]
        peat=peat:entry_point
    ''',
)
