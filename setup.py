#!/usr/bin/env python
from setuptools import setup, Command
from setuptools.extension import Extension
import sys, os, re, subprocess

__author__ = "Peter Maxwell"
__copyright__ = "Copyright 2007-2011, The Cogent Project"
__contributors__ = ["Peter Maxwell", "Gavin Huttley", "Matthew Wakefield",
                    "Greg Caporaso", "Daniel McDonald"]
__license__ = "GPL"
__version__ = "3.0a1"
__maintainer__ = "Peter Maxwell"
__email__ = "pm67nz@gmail.com"
__status__ = "Production"

# Check Python version, no point installing if unsupported version inplace
if sys.version_info < (3, 4):
    py_version = ".".join([str(n) for n in sys.version_info])
    raise RuntimeError("Python-3.4 or greater is required, Python-%s used." % py_version)


# Check Numpy version, no point installing if unsupported version inplace
try:
    import numpy
except ImportError:
    raise RuntimeError("Numpy required but not found.")

numpy_version = re.split("[^\d]", numpy.__version__)
numpy_version_info = tuple([int(i) for i in numpy_version if i.isdigit()])
if numpy_version_info < (1, 3):
    raise RuntimeError("Numpy-1.3 is required, %s found." % numpy_version)

# Find arrayobject.h on any system
numpy_include_dir = numpy.get_include()


# On windows with no commandline probably means we want to build an installer.
if sys.platform == "win32" and len(sys.argv) < 2:
    sys.argv[1:] = ["bdist_wininst"]


# A new command for predist, ie: pyrexc but no compile.
class NullCommand(Command):
    description = "Generate .c files from .pyx files"
    # List of option tuples: long name, short name (or None), and help string.
    user_options = [] #[('', '', ""),]
    def initialize_options (self):
        pass
    def finalize_options (self):
        pass
    def run (self):
        pass
        
class BuildDocumentation(NullCommand):
    description = "Generate HTML documentation and .c files"
    def run (self):
        # Restructured Text -> HTML
        try:
            import sphinx
        except ImportError:
            print("Failed to build html due to ImportErrors for sphinx")
            return
        cwd = os.getcwd()
        os.chdir('doc')
        subprocess.call(["make", "html"])
        os.chdir(cwd)
        print("Built index.html")

# Cython is now run via the Cythonize function rather than monkeypatched into 
# distutils, so these legacy commands don't need to do anything extra.
extra_commands = {
    'pyrexc': NullCommand,
    'cython': NullCommand,
    'predist': BuildDocumentation}


# Compiling Pyrex modules to .c and .so, if possible and necessary
try:
    if 'DONT_USE_CYTHON' in os.environ:
        raise ImportError
    from Cython.Compiler.Version import version
    version = tuple([int(v) \
        for v in re.split("[^\d]", version) if v.isdigit()])
    if version < (0, 17, 1):
        print("Your Cython version is too old")
        raise ImportError
except ImportError:
    source_suffix = '.c'
    cythonize = lambda x:x
    print("No Cython, will compile from .c files")
    for cmd in extra_commands:
        if cmd in sys.argv:
            print("'%s' command not available without Cython" % cmd)
            sys.exit(1)
else:
    from Cython.Build import cythonize
    source_suffix = '.pyx'


# Save some repetitive typing.  We have all compiled modules in place
# with their python siblings, so their paths and names are the same.
def CythonExtension(module_name, **kw):
    path = module_name.replace('.', '/')
    return Extension(module_name, [path + source_suffix], **kw)


short_description = "COmparative GENomics Toolkit 3"

# This ends up displayed by the installer
long_description = """Cogent3
A toolkit for statistical analysis of biological sequences.
Version %s.
""" % __version__

setup(
    name="cogent3",
    version=__version__,
    url="https://bitbucket.org/pycogent3/pycogent3",
    author="Gavin Huttley",
    author_email="gavin.huttley@anu.edu.au",
    description=short_description,
    long_description=long_description,
    platforms=["any"],
    license=["BSD"],
    keywords=["biology", "genomics", "statistics", "phylogeny", "evolution",
                "bioinformatics"],
    classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: GNU General Public License (GPL)",
            "Topic :: Scientific/Engineering :: Bio-Informatics",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Operating System :: OS Independent",
            ],
    packages=['cogent3', 'cogent3.align', 'cogent3.cluster',
              'cogent3.core', 'cogent3.data', 'cogent3.draw',
              'cogent3.evolve', 'cogent3.format', 'cogent3.maths',
              'cogent3.maths.matrix', 'cogent3.maths.stats', 'cogent3.parse',
              'cogent3.phylo', 'cogent3.recalculation', 'cogent3.util'],
    ext_modules=cythonize([
        CythonExtension("cogent3.align._compare"),
        CythonExtension("cogent3.align._pairwise_seqs"),
        CythonExtension("cogent3.align._pairwise_pogs"),
        CythonExtension("cogent3.evolve._solved_models"),
        CythonExtension("cogent3.evolve._likelihood_tree"),
        CythonExtension("cogent3.evolve._pairwise_distance"),
        CythonExtension("cogent3.maths._period"),
    ]),
    include_dirs = [numpy_include_dir],
    cmdclass = extra_commands,
    extras_require={"mpi": ["mpi4py"],
                    "all": ["matplotlib", "mpi4py", "pandas"]},
)
