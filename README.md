<p align="center">
  <h2 align="center">ICON Stats Service</h2>
</p>

[![loopchain](https://img.shields.io/badge/ICON-API-blue?logoColor=white&logo=icon&labelColor=31B8BB)](https://shields.io) [![GitHub Release](https://img.shields.io/github/release/sudoblockio/icon-stats.svg?style=flat)]() ![](https://github.com/sudoblockio/icon-stats/workflows/push-main/badge.svg?branch=main) [![codecov](https://codecov.io/gh/sudoblockio/icon-stats/branch/main/graph/badge.svg)](https://codecov.io/gh/sudoblockio/icon-stats) [![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

[//]: # (![Uptime]&#40;https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fsudoblockio%2Ficon-status-page%2Fmaster%2Fapi%2Fdev-stats-service%2Fuptime.json&#41;)

[Live API Docs](https://tracker.icon.community/api/v1/stats/docs)

Off chain indexer for the ICON Blockchain serving the **stats** for the [icon-explorer](https://github.com/sudoblockio/icon-explorer) and other related services. Service is broken up into API and worker components that are run as individual docker containers. It depends on data coming in from [icon-etl](https://github.com/sudoblockio/icon-extractor) and the databases behind the [ICON Tracker](https://tracker.icon.community/) with persistence on a postgres database.

### Deployment

Service can be run in the following ways:

1. Independently from this repo with docker compose:
```bash
docker-compose -f docker-compose.db.yml -f docker-compose.yml up -d
# Or alternatively
make up
```

2. With the whole stack from the main [icon-explorer](https://github.com/sudoblockio/icon-explorer) repo.

Run `make help` for more options.

### Development

For local development, you will want to run the `docker-compose.db.yml` as you develop. To run the tests,

```bash
make test
```

### License

Apache 2.0

