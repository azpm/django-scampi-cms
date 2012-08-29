from distutils.core import setup
import os

from libscampi import get_version

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

for dirpath, dirnames, filenames in os.walk('libscampi'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)
    elif filenames:
        prefix = dirpath[13:] # Strip "libscampi/" or "libscampi\"
        for f in filenames:
            data_files.append(os.path.join(prefix, f))

setup(name='django-scampi-cms',
    version=get_version().replace(' ', '-'),
    description='A django content management system.',
    author='Joey Leingang',
    author_email='leingang@arizona.edu',
    url='https://github.com/azpm/django-scampi-cms',
    package_dir={'libscampi': 'libscampi'},
    packages=packages,
    package_data={'libscampi': data_files},
    classifiers=['Development Status :: 4 - Beta',
                 'Environment :: Web Environment',
                 'Framework :: Django',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: BSD License',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
