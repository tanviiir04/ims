import requests
from datetime import datetime
from requests import send_warning

def check_sla_compliance():
    response = requests.get('http://localhost:5000/api/incidents/sla-metrics')
    metrics = response.json()
    
    if metrics['breached'] > 0:
        send_alert(f"{metrics['breached']} SLA breaches detected!")
    
    if metrics['at_risk'] > 0:
        send_warning(f"{metrics['at_risk']} tickets at risk of SLA breach")

def send_alert(message):
    # Implement your alerting logic
    print(f"ALERT: {message}")

if __name__ == '__main__':
    check_sla_compliance()