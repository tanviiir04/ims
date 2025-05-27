import requests
import psutil

SERVICES = ["mysql", "nginx"]

for service in SERVICES:
    if not any(service in p.name() for p in psutil.process_iter()):
        requests.post("http://localhost:5000/api/incidents", 
                     json={"title": f"Service {service} is down!"})