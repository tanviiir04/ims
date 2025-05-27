from backend.models    import db, Incident

from datetime import datetime, timedelta
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('incident_workflows.log'),
        logging.StreamHandler()
    ]
)

def apply_workflow_rules(incident: Incident) -> None:
    """Apply all business rules to an incident"""
    try:
        # Critical IT outages notify DevOps
        if (incident.priority == 'critical' and 
            incident.category == 'IT'):
            notify_devops(incident)
        
        # High priority incidents auto-assign
        if incident.priority in ('critical', 'high'):
            auto_assign_incident(incident)
        
        # Check SLA breaches
        check_sla_compliance(incident)
    except Exception as e:
        logging.error(f"Workflow failed for Incident #{incident.id}: {str(e)}")

def notify_devops(incident: Incident) -> None:
    alert_message = f"CRITICAL IT INCIDENT: {incident.title} (ID: {incident.id})"
    logging.critical(alert_message)

def auto_assign_incident(incident: Incident) -> None:
    if not incident.assigned_to:
        incident.assigned_to = "devops-team@yourcompany.com"
        logging.info(f"Auto-assigned Incident #{incident.id} to DevOps team")

def check_sla_compliance(incident: Incident) -> bool:
    try:
        if incident.status == 'resolved':
            return False
        if datetime.utcnow() > incident.sla_deadline:
            incident.priority = 'critical'
            breach_message = (
                f"SLA BREACH: Incident #{incident.id} '{incident.title}' "
                f"(Deadline: {incident.sla_deadline})"
            )
            logging.warning(breach_message)
            notify_sla_breach(incident)
            return True
        return False
    except Exception as e:
        logging.error(f"SLA check failed for Incident #{incident.id}: {str(e)}")
        return False

def notify_sla_breach(incident: Incident) -> None:
    try:
        logging.warning(
            f"Processing SLA breach for Incident #{incident.id} "
            f"(Current Priority: {incident.priority})"
        )
    except Exception as e:
        logging.error(f"Breach notification failed: {str(e)}")
