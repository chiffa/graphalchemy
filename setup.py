from distutils.core import setup

REQUIRES = ['bulbs<0.4']

setup(
    name='graphalchemy',
    version='0.1dev',
    description='Object-Graph Mapper (OGM) for Python '
                'compatible with Blueprint enabled graphs',
    long_description=open('README.md').read(),
    packages=['graphalchemy', 'graphalchemy.fixture', 'graphalchemy.tests'],
    classifiers=[
        'Development Status :: 0.1 - Dev',
        'Environment :: Web Environment',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Libraries :: Object Graph Mapper',
        'Programming Language :: Python',
    ],
    keywords='ogm graph blueprint',
    author='Antoine Durieux',
    author_email='adurieux@chefjerome.com',
    url='http://www.chefjerome.com/corporate',
    license='Apache 2.0',
    install_requires=REQUIRES,
    setup_requires=[],

)
