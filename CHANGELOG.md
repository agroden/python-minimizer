# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]
### Added
- New obfuscation module 
- Type hints for all functions

### Changed
- Logging uses a root logger now, no more checking verbosity
- Moved functional code to it's own module, now relies on main.py for driving

### Deprecated

### Removed

### Fixed

### Security


## [2.0.0] - 2020-07-19
### Changed
- Update README.md with better info
- Update setup.py to reflect supported versions
- Fully support Python 3 using Python 3 provided classes
  - Modified type enums and StringIO classes

### Removed
- No longer supports Python 2.7


## [1.0.2] - 2018-01-15
### Fixed
- Put spaces between numbers to ensure proper minification
- Ignore newlines inside token groups


## [1.0.1] - 2017-12-29
### Fixed
- Added file extension to LICENSE.txt for better functionality
- Include manifest file for distribution


## [1.0.0] - 2017-12-28
### Added
- setup.py for installation

### Changed
- Moved main code into a proper function


## [0.5.0] - 2017-12-25
### Added
- Updated comments and help strings
- Elaborated on command line usage
- Ignore pycharm files in .gitignore
- Ability to recursively minimize directory trees containing Python code
- Use logging module to print debug output

### Fixed
- Bracket counting to improve token group idenitification
- Fixed some keywords being spaced oddly - while correct, removal of whitespace in these situations made the code look wrong (minimizes less, but more readable)
- Merged fix for inconsistent user input / output directories


## [0.0.0] - 2017-12-21
### Added
- .gitignore, LICENSE, and README.md with basic usage examples
- WIP code for generating token groups in minimize.py