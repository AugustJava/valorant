import os
import json 
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from schemas import NewsCreate, TeamCreate

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
    

@app.post("/news")
async def create_news(news: NewsCreate):
    # 1. Читаем текущий список новостей
    data = load_json("news.json")

    # 2. Превращаем присланную новость в словарь и добавляем в список
    # (у тебя в JSON новости лежат в ключе "segments")
    new_post = news.dict()
    data["data"]["segments"].append(new_post)

    # 3. Сохраняем обновленный список обратно в файл
    with open("data/news.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return {"Message": "News added succesfully", "news": new_post}

@app.post("/rankings/{region}")
async def create_team(region: str, team: TeamCreate):
    filename = f"rankings-{region}.json"
    filepath = f"data/{filename}"

    # Проверяем, существует ли файл вообще
    if not os.path.exists(filepath):
        return {"error": f"Region '{region}' not found. Make sure data/{filename} exists"}
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    new_team = team.dict()
    data["data"].append(new_team)
    # Записываем обратно
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return {"Message": "Team added succesfully", "Team": new_team}

@app.delete("/rankings/{region}/{team_name}")
async def delete_team(region: str, team_name: str):
    filename = f"rankings-{region}.json"
    filepath = f"data/{filename}"
    
    if not os.path.exists(filepath):
        return {"error": "Region not found"}
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Создаем новый список, исключая команду с указанным именем
    original_count = len(data["data"])
    data["data"] = [t for t in data["data"] if t["team"]!= team_name]

    if len(data["data"]) == original_count:
        return {"error" : f"Team '{team_name}' not found"}
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return {"message" : f"Team '{team_name}' deleted successfuly"}

@app.patch("/rankings/{region}/{team_name}")
async def update_rank(region: str, team_name: str, new_rank: str):
    filename = f"rankings-{region}.json"
    filepath = f"data/{filename}"

    if not os.path.exists(filepath):
        return {"error" : "Region not found"}
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Ищем команду и меняем ей ранг
    found = False
    for t in data["data"]:
        if t["team"] == team_name:
            t["rank"] = new_rank
            found = True
            break
    if not found:
        return{"error":"Team not found"}
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return {"message":f"Rank for {team_name} updated to {new_rank}"}

if __name__=="__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)