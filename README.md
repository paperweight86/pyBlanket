# pyBlanket - automated wrapper generation
Utility to take C/C++ header files defining an interface and generate a wrapper for another language to use the library. Pipelined from Clang to a JSON dump (pyClump) and then pyBlanket uses pyStache (3rd party) to generate wrapper code.

# Early prototype (now)
pyClump C++ Visual Studio project file for a library and a given namespace, using the header files generates a json dump of the presumed exposed classes.

pyBlanket using pyStache and dump but only generates a simple header file for C++/CLI

# Next Steps
Plan the pipeline steps and configuration.
C++ -> [pyClump] -> Dump -> [pySharpBlanket] + Templates -> C++/CLI code -> [SharpMake??] -> C++/CLI project

# Prerequisites
- Python 2.7
- LLVM tools for windows for python access to libclang
- https://github.com/defunkt/pystache for templating
