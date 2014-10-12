import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

requires = [
    'django == 1.6',
    'django-filter',
    'pytz >= 0a',
    'humanize',
    'pydicom >= 0.9.7',
    'django-pagination',
    'xlsxwriter',
    'south',
    'celery >= 3.1',
    'argparse >= 1.2.1'
    ]

setup(
    name='OpenREM',
    version='0.4.3',
    packages=['openrem'],
    include_package_data=True,
    install_requires = requires,
    scripts=['openrem/scripts/openrem_rdsr.py','openrem/scripts/openrem_mg.py','openrem/scripts/openrem_ctphilips.py','openrem/scripts/openrem_ptsizecsv.py'],
    license='GPLv3 with additional permissions',  
    description='Radiation Exposure Monitoring for physicists',
    long_description=README,
    url='http://openrem.org/',
    author='Ed McDonagh',
    author_email='ed@openrem.org',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Healthcare Industry',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'Topic :: Scientific/Engineering :: Physics',
        ],
)
