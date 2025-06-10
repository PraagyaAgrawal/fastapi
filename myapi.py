from fastapi import FastAPI

app = FastAPI()

@app.get("/hello-world")
def print_true():
    return {"success":"true"}