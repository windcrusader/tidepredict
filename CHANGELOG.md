# Changelog
All changes to the project will be logged in this file.

## Unreleased / Development / TODO
* Metric -> imperial conversion (heathens)

## [0.4.4] - 2024-12-31
### Fixes
* directory creation for station info file
* deprecated numpy float removed and replaced with float64

## [0.4.3] - 2020-09-05
### Added
* csv graph data now outputs time as unix GMT timestamp

## [0.4.2] - 2020-09-03
### Added
* graph data in csv to .tidepredict directory

## [0.4.0] - 2020-09-02
### Added
* CSV mode
* Graph output
### Fixes
* Corrected problem with missing directory throwing errors
* Corrected issues with locations including spaces e.g "La Jolla"

## [0.3.0] - 2019-09-14
### Added
* README with some background info and usage information.
* Added the `-b l` option to generate a list of available stations.
* Added automatic finding of the station's timezone so that predictions are output in local time. This broke Python 2 support and I've decided not to support it anymore.
### Changed
* Overhauled and changed the way the module stores the constituents so that it now stores additional information about the station such as latitude and longitude. This is saved as a JSON file for human and machine compatibility.
