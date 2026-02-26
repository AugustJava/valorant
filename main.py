import json 
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ЭТО ВАЖНО: Разрешаем фронтенду подключаться к нам
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # В будущем заменим на адрес сайта друга
    allow_methods=["*"],
    allow_headers=["*"]
)

def load_json(filename: str):
    with open(f"data/{filename}", "r", encoding="utf-8") as f:
        return json.load(f)
    
@app.get("/news")
async def get_news():
    data = load_json("news.json")
    return data

@app.get("/ranking/{region}")
async def get_rankings(region: str):
    # region будет принимать значения: eu, na, ap, br и т.д.
    filename = f"rankings-{region}.json"
    try:
        data = load_json(filename)
        return data
    except FileNotFoundError:
        return {"error":"Region not found"}
if __name__=="__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)