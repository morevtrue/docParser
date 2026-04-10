from fastapi import FastAPI

app = FastAPI(title="DocParser API")


@app.get("/api/health")
def health_check():
    """Health-check эндпоинт."""
    return {"status": "ok"}
