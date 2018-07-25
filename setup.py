from setuptools import setup, find_packages

setup(
    name='webeditor',
    version='0.7.0',
    author='shenli',
    author_email='shenli1120@qq.com',
    include_package_data=True,
    packages=find_packages(),
    # packages=find_packages(where='.', exclude=(), include=('*',)),
    # url='http://pypi.python.org/pypi/web-editor/',
    url='https://test.pypi.org/pypi/webeditor/',
    license='LICENSE.txt',
    entry_points={
        'console_scripts': [
            'webeditor=webeditor.server:start_server',
        ]
    },
    description='Useful towel-related stuff.',
    long_description=open('README.txt').read(),
    setup_requires=['tornado'],
    install_requires=["tornado"],
)
