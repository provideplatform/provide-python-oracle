import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='prvdoracle',
    version='0.0.1',
    author='Kyle Thomas',
    author_email='kyle@provide.services',
    description='Provide oracle base architecture and runloop',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/provideservices/provide-oracle',
    packages=setuptools.find_packages(),
    install_requires=[
        'backports-abc',
        'prvd',
        'tornado',
    ],
    classifiers=[
    ],
    entry_points = {
        'console_scripts': [],
    },
)
