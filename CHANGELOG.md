# Changelog
All changes to the project will be logged in this file.

## Unreleased / Development / TODO
* Graphing of tide predictions
* csv mode
* Metric -> imperial conversion (heathens)


## [0.3.0] - 2019-09-14
### Added
* README with some background info and usage information.
* Added the `-b l` option to generate a list of available stations.
* Added automatic finding of the station's timezone so that predictions are output in local time. This broke Python 2 support and I've decided not to support it anymore.
### Changed
* Overhauled and changed the way the module stores the constituents so that it now stores additional information about the station such as latitude and longitude. This is saved as a JSON file for human and machine compatibility.
