from cx_Freeze import setup, Executable
from nsncdrparser import __version__

# Dependencies are automatically detected, but it might need
# fine tuning.


base = 'Console'
included_files = ['sacdr.patterns','scdr.patterns']

buildOptions = dict(packages = [], excludes = [],include_files=included_files)
                   
executables = [
    Executable('nsncdrparser.py', base=base)
]

setup(name='nsncdrparser',
      version = __version__,
      description = 'A tool can parse and search NSN CDR file',
      options = dict(build_exe = buildOptions),
      executables = executables)
