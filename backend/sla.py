from backend.models    import Incident

from datetime import datetime, timedelta

def calculate_sla_metrics():
    incidents = Incident.query.filter(Incident.status != 'resolved').all()
    metrics = {
        'breached': 0,
        'at_risk': 0,
        'on_track': 0
    }
    for incident in incidents:
        time_remaining = incident.sla_deadline - datetime.utcnow()
        if datetime.utcnow() > incident.sla_deadline:
            metrics['breached'] += 1
        elif time_remaining < timedelta(hours=1):
            metrics['at_risk'] += 1
        else:
            metrics['on_track'] += 1
    return metrics
