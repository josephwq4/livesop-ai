from fastapi import FastAPI

# Bare Metal Isolation: No Middlewares, No Auth, No Routers, No DotEnv
app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok", "mode": "bare_metal"}

@app.get("/")
def root():
    return {"message": "Bare Metal Mode Active"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
