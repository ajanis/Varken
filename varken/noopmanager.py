from logging import getLogger


class NoopDBManager(object):
    def __init__(self, prometheus_exporter=None):
        self.logger = getLogger()
        self.prometheus_exporter = prometheus_exporter

    def write_points(self, data):
        if not self.prometheus_exporter:
            return
        try:
            self.prometheus_exporter.observe_points(data)
        except Exception as e:
            self.logger.error('Error exporting Prometheus metrics. Error: %s', e)
