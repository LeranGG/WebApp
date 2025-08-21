import json, urllib.parse, datetime
from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from funcs import get_db_pool
from fastapi.encoders import jsonable_encoder
from test import prices, update
from decimal import Decimal, getcontext

getcontext().prec = 50

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Click(BaseModel):
    quantity: int


@app.post("/get-user-info")
async def get_user_id(initData: str = Form(...)):
    try:
        params = dict(urllib.parse.parse_qsl(initData))

        # Декодируем JSON-параметр user
        user_json = urllib.parse.unquote(params.get("user", "{}"))
        user_data = json.loads(user_json)

        # Теперь можно взять user_id из user_data
        tg_id = user_data.get("id")

        pool = await get_db_pool()
        async with pool.acquire() as conn:
            users = await conn.fetchrow('SELECT * FROM stats WHERE userid = $1', tg_id)
            if users == None:
                await conn.execute('INSERT INTO stats (userid) VALUES ($1)', tg_id)
            else:
                pass
        
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            stats = await conn.fetchrow('SELECT bal, room, name, pc FROM stats WHERE userid = $1', tg_id)
        return JSONResponse(content=jsonable_encoder({
            "name": stats[2],
            "room": stats[1],
            "balance": stats[0],
            "pcs": stats[3]
        }))
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/api/top")
async def receive_top():
    try:        
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            top = await conn.fetch('SELECT name, bal, userid FROM stats ORDER BY bal DESC LIMIT 5')
        return JSONResponse(content=jsonable_encoder({
            "users": top
        }))

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/api/shop_room")
async def receive_shop_room(initData: str = Form(...)):
    try:
        params = dict(urllib.parse.parse_qsl(initData))

        # Декодируем JSON-параметр user
        user_json = urllib.parse.unquote(params.get("user", "{}"))
        user_data = json.loads(user_json)

        # Теперь можно взять user_id из user_data
        tg_id = user_data.get("id")
        
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            room = await conn.fetchval('SELECT room FROM stats WHERE userid = $1', tg_id)
        return JSONResponse(content=jsonable_encoder({
            "lvl": room
        }))

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/api/rename")
async def receive_rename(initData: str = Form(...), newName: str = Form(...)):
    try:
        params = dict(urllib.parse.parse_qsl(initData))

        # Декодируем JSON-параметр user
        user_json = urllib.parse.unquote(params.get("user", "{}"))
        user_data = json.loads(user_json)

        # Теперь можно взять user_id из user_data
        tg_id = user_data.get("id")
        
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            await conn.execute('UPDATE stats SET name = $1 WHERE userid = $2', newName, tg_id)
        return {"status": "ok"}

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/api/buy_room")
async def buy_room(initData: str = Form(...)):
    try:
        params = dict(urllib.parse.parse_qsl(initData))

        # Декодируем JSON-параметр user
        user_json = urllib.parse.unquote(params.get("user", "{}"))
        user_data = json.loads(user_json)

        # Теперь можно взять user_id из user_data
        tg_id = user_data.get("id")
        
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            stats = await conn.fetchrow('SELECT room, bal, income FROM stats WHERE userid = $1', tg_id)
            for el in update:
                b = Decimal(str(stats[1]))
                if stats[1] >= el[1] and stats[0]+1 == el[0] and stats[2] >= el[2]:
                    print(1)
                    await conn.execute('UPDATE stats SET bal = $1, room = $2 WHERE userid = $3', b-el[1], stats[0]+1, tg_id)
                    data = '✅ Вы успешно прокачали комнату'
                    if el[0] == 2:
                        ref = await conn.fetchval('SELECT ref FROM stats WHERE userid = $1', tg_id)
                        if ref != None and ref > 0:
                            prem = await conn.fetchval('SELECT premium FROM stats WHERE userid = $1', ref)
                            if prem > datetime.datetime.today():
                                await conn.execute('UPDATE stats SET premium = $1 WHERE userid = $2', prem + datetime.timedelta(hours=12), ref)
                            else:
                                await conn.execute('UPDATE stats SET premium = $1 WHERE userid = $2', datetime.datetime.today() + datetime.timedelta(hours=12), ref)
                elif stats[1] < el[1] and stats[0]+1 == el[0]:
                    print(2)
                    data = '❌ У вас не хватает $'
                elif stats[2] < el[2] and stats[0]+1 == el[0]:
                    print(3)
                    data = f'❌ У вас недостаточно дохода, нужно: {el[2]}'
        return data

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/api/shop_pc")
async def shop_pc(initData: str = Form(...)):
    try:
        params = dict(urllib.parse.parse_qsl(initData))

        # Декодируем JSON-параметр user
        user_json = urllib.parse.unquote(params.get("user", "{}"))
        user_data = json.loads(user_json)

        # Теперь можно взять user_id из user_data
        tg_id = user_data.get("id")
        
        result = []
        for level, income, price in prices:
            result.append({
                "level": level,
                "income": income,
                "price": price,
                "name": f"Компьютер {level}",
                "description": f"💰 Доход: {income}₽ / Цена: {price}₽"
            })
        return result
        
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/api/buy_pc")
async def shop_pc(initData: str = Form(...), quantity: int = Form(...), lvl: int = Form(...)):
    try:
        params = dict(urllib.parse.parse_qsl(initData))

        # Декодируем JSON-параметр user
        user_json = urllib.parse.unquote(params.get("user", "{}"))
        user_data = json.loads(user_json)

        # Теперь можно взять user_id из user_data
        tg_id = user_data.get("id")
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            stats = await conn.fetchrow('SELECT bal, room, pc, income FROM stats WHERE userid = $1', tg_id)
            for el in prices:
                if lvl == el[0] and stats[0] >= el[2]*quantity and stats[2]+quantity <= stats[1]*5 and stats[1] >= lvl:
                    bal = Decimal(str(stats[0]))
                    income = Decimal(str(stats[3]))
                    pc_inc = Decimal(str(el[1]))
                    await conn.execute('UPDATE stats SET bal = $1, pc = $2, income = $3, all_pcs = all_pcs + $4 WHERE userid = $5', bal-el[2]*quantity, stats[2]+quantity, income+pc_inc*quantity, quantity, tg_id)
                    for i in range(0, quantity):
                        await conn.execute('INSERT INTO pc (userid, lvl, income) VALUES ($1, $2, $3)', tg_id, lvl, pc_inc)
                    return [f'✅ Вы успешно купили x{quantity} Компьютер {lvl} ур. за {el[2]*quantity}$']
                elif lvl == el[0] and stats[0] < el[2]*quantity:
                    return ['❌ У вас не достаточно средств!']
                elif lvl == el[0] and stats[2]+quantity > stats[1]*5:
                    return ['❌ У вас не хватает места. Чтобы увеличить количество мест улучшите комнату!']
                elif lvl == el[0] and stats[1] < lvl:
                    return ['❌ Этот компьютер вам не доступен!']
        
        
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


app.mount("/", StaticFiles(directory="public", html=True), name="static")