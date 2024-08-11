## [2.0.1-beta.1](https://github.com/mguyard/appdaemon-iopoolpumpmanager/compare/v2.0.0...v2.0.1-beta.1) (2024-07-21)


### Bug Fixes

* iopool recommanded_duration was not read at each change, due to that, calculated duration and all handlers wasn't updated. Now in this release, each iopool recommanded_duration is tracked and app is reload to ajust handler. In case filtration is running and during a slot, app analyze if new end time of slot is in past to stop filtration before reloading app to avoid poolpump to stop only on the end of next slot (too many filtration not needed) ([cfd1094](https://github.com/mguyard/appdaemon-iopoolpumpmanager/commit/cfd109462d768e9e597a74997223180ba72d7a79))

# [2.0.0](https://github.com/mguyard/appdaemon-iopoolpumpmanager/compare/v1.0.7...v2.0.0) (2024-06-21)


### Bug Fixes

* Update recommended filtration duration entity with source = AD-iopoolPumpManager ([7c8e632](https://github.com/mguyard/appdaemon-iopoolpumpmanager/commit/7c8e6324c3b8efbbf51e83c2ce6a1db5f9c30776))
* Update recommended filtration duration entity with source = AD-iopoolPumpManager ([23451e2](https://github.com/mguyard/appdaemon-iopoolpumpmanager/commit/23451e23e16712f60045dada3b0a7a5a49c4662c))


### Features

* Adding configuration parameter pool_name when using multiple pool ([506a79c](https://github.com/mguyard/appdaemon-iopoolpumpmanager/commit/506a79c9765c9591c7d1fcf09eb86f04dd55a047))


### BREAKING CHANGES

* You need to update iopool Pump Manager, stop AppDaemon addon, restart Home Assistant and start AppDaemon addon to recreate the calculated filtration duration entity

# [2.0.0-beta.2](https://github.com/mguyard/appdaemon-iopoolpumpmanager/compare/v2.0.0-beta.1...v2.0.0-beta.2) (2024-06-18)


### Bug Fixes

* Update recommended filtration duration entity with source = AD-iopoolPumpManager ([7c8e632](https://github.com/mguyard/appdaemon-iopoolpumpmanager/commit/7c8e6324c3b8efbbf51e83c2ce6a1db5f9c30776))
* Update recommended filtration duration entity with source = AD-iopoolPumpManager ([23451e2](https://github.com/mguyard/appdaemon-iopoolpumpmanager/commit/23451e23e16712f60045dada3b0a7a5a49c4662c))

# [2.0.0-beta.1](https://github.com/mguyard/appdaemon-iopoolpumpmanager/compare/v1.0.7...v2.0.0-beta.1) (2024-06-18)


### Features

* Adding configuration parameter pool_name when using multiple pool ([506a79c](https://github.com/mguyard/appdaemon-iopoolpumpmanager/commit/506a79c9765c9591c7d1fcf09eb86f04dd55a047))


### BREAKING CHANGES

* ou need to update iopool Pump Manager, stop AppDaemon addon, restart Home Assistant and start AppDaemon addon to recreate the calculated filtration duration entity

## [1.0.7](https://github.com/mguyard/appdaemon-iopoolpumpmanager/compare/v1.0.6...v1.0.7) (2024-06-16)


### Bug Fixes

* Round elapsed time to the nearest minute in end_filtration event ([3167126](https://github.com/mguyard/appdaemon-iopoolpumpmanager/commit/31671262416e9361df5067adf8efdaa95e840198))

## [1.0.7-beta.1](https://github.com/mguyard/appdaemon-iopoolpumpmanager/compare/v1.0.6...v1.0.7-beta.1) (2024-06-12)


### Bug Fixes

* Round elapsed time to the nearest minute in end_filtration event ([3167126](https://github.com/mguyard/appdaemon-iopoolpumpmanager/commit/31671262416e9361df5067adf8efdaa95e840198))

## [1.0.6](https://github.com/mguyard/appdaemon-iopoolpumpmanager/compare/v1.0.5...v1.0.6) (2024-06-05)


### Bug Fixes

* Change module name to avoid collision with my others apps ([bf285c3](https://github.com/mguyard/appdaemon-iopoolpumpmanager/commit/bf285c3745cda35fab56e982286842771a46cb9b))

## [1.0.6-beta.1](https://github.com/mguyard/appdaemon-iopoolpumpmanager/compare/v1.0.5...v1.0.6-beta.1) (2024-06-05)


### Bug Fixes

* Change module name to avoid collision with my others apps ([bf285c3](https://github.com/mguyard/appdaemon-iopoolpumpmanager/commit/bf285c3745cda35fab56e982286842771a46cb9b))

## [1.0.5](https://github.com/mguyard/appdaemon-iopoolpumpmanager/compare/v1.0.4...v1.0.5) (2024-06-05)


### Bug Fixes

* Resolve issue with config.filtration_summer.max_duration that was required but it's an optional configuration ([1ae2edb](https://github.com/mguyard/appdaemon-iopoolpumpmanager/commit/1ae2edb95eebefbd02f676bf9a01b4f542614d66))

## [1.0.5-beta.1](https://github.com/mguyard/appdaemon-iopoolpumpmanager/compare/v1.0.4...v1.0.5-beta.1) (2024-06-05)


### Bug Fixes

* Resolve issue with config.filtration_summer.max_duration that was required but it's an optional configuration ([1ae2edb](https://github.com/mguyard/appdaemon-iopoolpumpmanager/commit/1ae2edb95eebefbd02f676bf9a01b4f542614d66))

## [1.0.4](https://github.com/mguyard/appdaemon-iopoolpumpmanager/compare/v1.0.3...v1.0.4) (2024-06-05)


### Bug Fixes

* Change appdaemon main folder name to match HACS requirements ([c5533ad](https://github.com/mguyard/appdaemon-iopoolpumpmanager/commit/c5533ad91faa1aad17eb82ea460c846bd83b5b3f))
* Change appdaemon main folder name to match HACS requirements ([f8c8861](https://github.com/mguyard/appdaemon-iopoolpumpmanager/commit/f8c8861e01e799c8f396aa0dac81d614b4e8bfff))

## [1.0.4-beta.2](https://github.com/mguyard/appdaemon-iopoolpumpmanager/compare/v1.0.4-beta.1...v1.0.4-beta.2) (2024-06-05)


### Bug Fixes

* Change appdaemon main folder name to match HACS requirements ([c5533ad](https://github.com/mguyard/appdaemon-iopoolpumpmanager/commit/c5533ad91faa1aad17eb82ea460c846bd83b5b3f))

## [1.0.4-beta.1](https://github.com/mguyard/appdaemon-iopoolpumpmanager/compare/v1.0.3...v1.0.4-beta.1) (2024-06-05)


### Bug Fixes

* Change appdaemon main folder name to match HACS requirements ([f8c8861](https://github.com/mguyard/appdaemon-iopoolpumpmanager/commit/f8c8861e01e799c8f396aa0dac81d614b4e8bfff))

## [1.0.3](https://github.com/mguyard/appdaemon-iopoolpumpmanager/compare/v1.0.2...v1.0.3) (2024-06-05)


### Bug Fixes

* Change appdaemon repository structure to match HACS requirements ([124f34e](https://github.com/mguyard/appdaemon-iopoolpumpmanager/commit/124f34e923e3e53bf1e98323b54fefd86ac82b75))

## [1.0.3-beta.1](https://github.com/mguyard/appdaemon-iopoolpumpmanager/compare/v1.0.2...v1.0.3-beta.1) (2024-06-05)


### Bug Fixes

* Change appdaemon repository structure to match HACS requirements ([124f34e](https://github.com/mguyard/appdaemon-iopoolpumpmanager/commit/124f34e923e3e53bf1e98323b54fefd86ac82b75))

## [1.0.2](https://github.com/mguyard/appdaemon-iopoolpumpmanager/compare/v1.0.1...v1.0.2) (2024-05-25)


### Bug Fixes

* Updating doc for HACS ([fa8c487](https://github.com/mguyard/appdaemon-iopoolpumpmanager/commit/fa8c48767b639d9f1bbe78dbb0efbd9ad745dcd2))

## [1.0.2-beta.1](https://github.com/mguyard/appdaemon-iopoolpumpmanager/compare/v1.0.1...v1.0.2-beta.1) (2024-05-25)


### Bug Fixes

* Updating doc for HACS ([fa8c487](https://github.com/mguyard/appdaemon-iopoolpumpmanager/commit/fa8c48767b639d9f1bbe78dbb0efbd9ad745dcd2))

# [1.0.1](https://github.com/mguyard/appdaemon-iopoolpumpmanager/compare/v1.0.0...v1.0.1) (2024-05-25)


### Bug Fixes

* set calculated duration also for active-winter mode ([8cb50f5](https://github.com/mguyard/appdaemon-iopoolpumpmanager/commit/8cb50f53f29107d14cbfaa47014320774822f35a))

# [1.0.0-beta.2](https://github.com/mguyard/appdaemon-iopoolpumpmanager/compare/v1.0.0-beta.1...v1.0.0-beta.2) (2024-05-25)


### Bug Fixes

* set calculated duration also for active-winter mode ([8cb50f5](https://github.com/mguyard/appdaemon-iopoolpumpmanager/commit/8cb50f53f29107d14cbfaa47014320774822f35a))

# 1.0.0 (2024-05-25)


### Features


* Initial version ([f79c7e7](https://github.com/mguyard/appdaemon-iopoolpumpmanager/commit/f79c7e767a9f97ef59f57833f352a13ba250a1c3))

# 1.0.0-beta.1 (2024-05-25)


### Features

* Initial version ([f79c7e7](https://github.com/mguyard/appdaemon-iopoolpumpmanager/commit/f79c7e767a9f97ef59f57833f352a13ba250a1c3))
