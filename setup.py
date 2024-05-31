import setuptools
import f1_24_telemetry

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='f1-24-telemetry',
    version=f1_24_telemetry.__version__,
    author='Xavier Dubuc',
    author_email='contact@xavierdubuc.com',
    description='Decode F1-24 telemetry data.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/chrishannam/f1-24-telemetry',
    packages=setuptools.find_packages(exclude=('tests', 'examples')),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    include_package_data=True,
    python_requires='>=3.7',
)
