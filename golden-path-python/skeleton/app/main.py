"""
${{ values.serviceName }}
 
Microservicio Python generado con el Golden Path de la plataforma.
"""
 
from fastapi import FastAPI
 
SERVICE_NAME = "${{ values.serviceName }}"
OWNER = "${{ values.owner }}"
 
app = FastAPI(title=SERVICE_NAME)
 
 
@app.get("/health")
def health():
    """Health check usado por las probes de Kubernetes."""
    return {"status": "UP", "service": SERVICE_NAME}
 
 
@app.get("/")
def root():
    return {
        "service": SERVICE_NAME,
        "owner": OWNER,
        "message": "Generado con el Golden Path de la plataforma",
    }