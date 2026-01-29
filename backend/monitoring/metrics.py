import time
from functools import wraps
from collections import defaultdict
from datetime import datetime


class MetricsCollector:
    """Simple metrics collector for Prometheus-compatible output."""
    
    def __init__(self):
        self.counters = defaultdict(int)
        self.gauges = defaultdict(float)
        self.histograms = defaultdict(list)
        self.start_time = time.time()
    
    def increment(self, name, value=1, labels=None):
        """Increment a counter."""
        key = self._make_key(name, labels)
        self.counters[key] += value
    
    def set_gauge(self, name, value, labels=None):
        """Set a gauge value."""
        key = self._make_key(name, labels)
        self.gauges[key] = value
    
    def observe(self, name, value, labels=None):
        """Record a histogram observation."""
        key = self._make_key(name, labels)
        self.histograms[key].append(value)
    
    def _make_key(self, name, labels):
        """Create a unique key for metrics with labels."""
        if labels:
            label_str = ','.join(f'{k}="{v}"' for k, v in sorted(labels.items()))
            return f'{name}{{{label_str}}}'
        return name
    
    def to_prometheus(self):
        """Export metrics in Prometheus format."""
        lines = []
        
        # Add uptime
        uptime = time.time() - self.start_time
        lines.append(f'# HELP agritech_uptime_seconds Application uptime in seconds')
        lines.append(f'# TYPE agritech_uptime_seconds gauge')
        lines.append(f'agritech_uptime_seconds {uptime:.2f}')
        lines.append('')
        
        # Counters
        for key, value in self.counters.items():
            lines.append(f'# TYPE {key.split("{")[0]} counter')
            lines.append(f'{key} {value}')
        
        # Gauges
        for key, value in self.gauges.items():
            lines.append(f'# TYPE {key.split("{")[0]} gauge')
            lines.append(f'{key} {value}')
        
        # Histograms (simplified - just count and sum)
        for key, values in self.histograms.items():
            base_name = key.split('{')[0]
            lines.append(f'# TYPE {base_name} histogram')
            lines.append(f'{key}_count {len(values)}')
            lines.append(f'{key}_sum {sum(values):.4f}')
        
        return '\n'.join(lines)


# Global metrics collector
metrics = MetricsCollector()


def track_request_metrics(f):
    """Decorator to track request metrics."""
    @wraps(f)
    def decorated(*args, **kwargs):
        start = time.time()
        try:
            result = f(*args, **kwargs)
            metrics.increment('agritech_requests_total', labels={'status': 'success'})
            return result
        except Exception as e:
            metrics.increment('agritech_requests_total', labels={'status': 'error'})
            raise
        finally:
            duration = time.time() - start
            metrics.observe('agritech_request_duration_seconds', duration)
    return decorated
