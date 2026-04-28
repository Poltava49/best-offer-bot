import redis
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="static")


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


@app.get("/front", response_class=HTMLResponse)
def read_root(request: Request, age: int, name: str = "Anton"):
    if age:
        r.json().set(f"user:{name}", "$", {"name": name, "age": age})
        return templates.TemplateResponse(
            request=request, name="front.html", context={"name": name, "age": age}
        )
    age_cached = r.json().get(f"user:{name}", "$.age")
    if age_cached:
        return templates.TemplateResponse(
            request=request,
            name="front.html",
            context={"name": name, "age": age_cached},
        )
    else:
        return templates.TemplateResponse(
            request=request, name="front.html", context={"name": name}
        )
