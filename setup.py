from distutils.core import setup
from distutils.extension import Extension

from Cython.Build import cythonize
from Cython.Distutils import build_ext

# Compile using
# python setup.py build_ext --inplace

ext_modules = [
    Extension("*", ["implementation/*.py"]),
    Extension("*", ["implementation/console/*.py"]),
]

setup(
    name="Levin Program Search Implementation",
    cmdclass={"build_ext": build_ext},
    ext_modules=cythonize(ext_modules, compiler_directives={"language_level": "3"}),
)
