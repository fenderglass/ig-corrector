from setuptools import setup
from setuptools.extension import Extension
from Cython.Distutils import build_ext

setup(name="calign",
      version='0.1',
      description='Global and local sequence alignment implemented in C for speed.',
      author='Fredrik Appelros, Carl Ekerot',
      author_email='fredrik.appelros@gmail.com, kalle@implode.se',
      url='https://github.com/FredrikAppelros/align',
      install_requires=['numpy', 'cython'],
      cmdclass = {'build_ext': build_ext},
      ext_modules = [Extension('align', ['src/align.pyx', 'src/calign.c'])],
)
