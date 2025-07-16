from setuptools import setup, find_packages

setup(
    name='isq_suite',
    version='1.0.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        # Tus dependencias principales
        'numpy',
        'pandas',
        'matplotlib',
        # Agrega aquí otras dependencias clave
    ],
    entry_points={
        'console_scripts': [
            'isq-suite = suite.launcher:main',
            'isq-inmr = suite.apps.inmr.maini:main',
            'isq-qnmr = suite.apps.qnmr.mainq:main',
            'isq-snmr = suite.apps.snmr.mains:main'
        ]
    },
    include_package_data=True,
    package_data={
        'suite': ['resources/icons/*.ico'],
    },
)
