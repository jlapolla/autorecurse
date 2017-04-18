from setuptools import find_packages, setup


setup(
    name='autorecurse',
    version='1.0.0a1',
    description='Wraps the make build utility and automatically calls make recursively on makefiles in subdirectories.',
    author='Justin LaPolla',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=['antlr4-python3-runtime ~= 4.5, < 4.6'],
    package_data={'autorecurse': ['config/*.txt']},
    zip_safe=False
        )


