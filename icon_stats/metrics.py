from prometheus_client import Counter, Gauge


class Metrics:
    def __init__(self):
        self.cron_ran = Counter(
            "cron_ran",
            "Number of times a cron ran",
        )


prom_metrics = Metrics()
