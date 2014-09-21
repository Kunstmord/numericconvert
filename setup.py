from distutils.core import setup

setup(name='numericconvert',
      version='0.1',
      description='Library for conversion of numeric Python code to C++ code',
      author='George Oblapenko',
      author_email='kunstmord@kunstmord.com',
      url='https://github.com/Kunstmord/kineticlib',
      license="MIT",
      packages=['numericconvert'],
      include_package_data=True,
      classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        ],
      long_description = """\
      NumericConvert
      ==============

      A small utility library for converting numeric code written in Python to numeric code written in C++.


      What is planned
      ===============

      * Support for file input/output (calling from command line and dumping result to file)

      * Inferring input types from type annotations

      * A dictionary of standard mappings and support for custom mappings (substitutions)
      """
      )