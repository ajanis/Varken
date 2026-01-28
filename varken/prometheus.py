import re
from logging import getLogger

try:
    from prometheus_client import CollectorRegistry, Gauge, start_http_server
    PROMETHEUS_AVAILABLE = True
except Exception:
    PROMETHEUS_AVAILABLE = False

_INVALID_METRIC_CHAR_RE = re.compile(r'[^a-zA-Z0-9_]')


def _sanitize_metric_name(name):
    sanitized = _INVALID_METRIC_CHAR_RE.sub('_', name.lower())
    if sanitized and sanitized[0].isdigit():
        sanitized = f'_{sanitized}'
    return sanitized


class PrometheusExporter(object):
    def __init__(self, addr='0.0.0.0', port=9595, prefix='varken'):
        self.logger = getLogger()
        self.enabled = False
        self.registry = None
        self.metrics = {}
        self.metric_labels = {}
        self.metric_label_values = {}
        self.logged_label_mismatch = set()
        self.prefix = _sanitize_metric_name(prefix)
        self.logged_non_numeric = set()

        if not PROMETHEUS_AVAILABLE:
            self.logger.error('Prometheus client is not installed. Install prometheus-client to enable metrics.')
            return

        try:
            self.registry = CollectorRegistry()
            start_http_server(port, addr=addr, registry=self.registry)
        except Exception as e:
            self.logger.error('Failed to start Prometheus metrics endpoint on %s:%s. Error: %s', addr, port, e)
            return

        self.enabled = True
        self.logger.info('Prometheus metrics endpoint enabled on %s:%s/metrics', addr, port)

    def observe_points(self, data):
        if not self.enabled:
            return

        points = data if isinstance(data, list) else [data]
        batch_series = {}
        for point in points:
            if not isinstance(point, dict):
                continue

            measurement = point.get('measurement')
            fields = point.get('fields') or {}
            tags = point.get('tags') or {}

            if not measurement or not fields:
                continue

            for field_name, value in fields.items():
                metric_name = self._metric_name(measurement, field_name)
                gauge = self._get_gauge(metric_name, tags)
                if gauge is None:
                    continue

                label_names = self.metric_labels[metric_name]
                label_values = [str(tags.get(label, '')) for label in label_names]
                label_key = tuple(label_values)
                batch_series.setdefault(metric_name, set()).add(label_key)
                self.metric_label_values.setdefault(metric_name, set()).add(label_key)

                try:
                    numeric_value = float(value)
                except (TypeError, ValueError):
                    if value is None:
                        continue
                    if metric_name not in self.logged_non_numeric:
                        self.logger.info(
                            'Prometheus metric %s received non-numeric value; exporting as 1.',
                            metric_name,
                        )
                        self.logged_non_numeric.add(metric_name)
                    numeric_value = 1.0

                gauge.labels(*label_values).set(numeric_value)

        for metric_name, seen_labels in batch_series.items():
            gauge = self.metrics.get(metric_name)
            if not gauge:
                continue
            for label_key in self.metric_label_values.get(metric_name, set()):
                if label_key not in seen_labels:
                    gauge.labels(*label_key).set(0)

    def _metric_name(self, measurement, field_name):
        base = _sanitize_metric_name(f'{measurement}_{field_name}')
        if self.prefix:
            return f'{self.prefix}_{base}'
        return base

    def _get_gauge(self, metric_name, tags):
        label_names = self.metric_labels.get(metric_name)
        if label_names is None:
            label_names = sorted(tags.keys())
            self.metric_labels[metric_name] = label_names
            try:
                self.metrics[metric_name] = Gauge(
                    metric_name,
                    f'Varken metric {metric_name}',
                    label_names,
                    registry=self.registry,
                )
            except ValueError as e:
                self.logger.error('Failed to register Prometheus metric %s. Error: %s', metric_name, e)
                self.metric_labels.pop(metric_name, None)
                return None
        else:
            extra_labels = set(tags.keys()) - set(label_names)
            if extra_labels and metric_name not in self.logged_label_mismatch:
                self.logger.warning(
                    'Prometheus metric %s received unexpected labels %s; ignoring extras.',
                    metric_name,
                    ','.join(sorted(extra_labels)),
                )
                self.logged_label_mismatch.add(metric_name)

        return self.metrics[metric_name]
