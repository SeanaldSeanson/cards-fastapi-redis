import secrets, time
import redis, hiredis
from fastapi import FastAPI
from pydantic import BaseModel
from app.cards_helpers import *
from enum import IntEnum

class SortBy(IntEnum):
    NAME = 0
    DATE = 1

class GameCreationInfo(BaseModel):
    player_name: str = None
    name: str = None
    desc: str = None
    hand_size: int = 8
    max_players: int = 8
    decks: list = []
    public: bool = True

app = FastAPI()

r = redis.Redis(host="localhost", port=6379, db=0, health_check_interval=30,
        decode_responses=True)

z_add_unique = ""
with open("app/redis/z_add_unique.lua") as script_file:
    z_add_unique = r.register_script(script_file.read())
    script_file.close()

async def zaddUnique(key: str, nbytes: int = 4, score: float = time.time()):
    return z_add_unique(keys=[key], args=[nbytes, score, secrets.randbits(32)])

def mergeDict(x: dict, y: dict):
    x.update(y)
    return x

async def hUpdate(h, data: dict):
    pipe = r.pipeline()
    for dkey in data.keys():
        pipe.hset(h, dkey, data[key])
    pipe.execute()

async def makePlayer(game_id: str, name: str = ""):
    pipe = r.pipeline()
    player_id = zaddUnique("players")
    player_hash = "player_" + player_id
    pipe.hset(player_hash, "game_id", game_id)

    secret = secrets.token_urlsafe(256)
    pipe.hset(player_hash, "secret", secret)

    pipe.expire(player_hash, 1200)
    pipe.execute()
    return (player_id, secret)

async def makeGame(data: dict):
    pipe = r.pipeline()

    # Generate a unique game_id
    game_id = zaddUnique("games", 4)

    game_hash = "game_" + game_id

    # Pop player_name from data and use it to create a player entry, then
    # replace it with the new player's player_id.
    player_id, secret = await makePlayer(game_id, data.pop("player_name", ""))
    data["host"] = player_id

    for k in data.keys():
        pipe.hset(game_id, k, data[k])

    game_players_set = "game_players:" + game_id
    pipe.sadd("game_players:" + game_id, player_id)

    pipe.expire(game_hash, 1200)
    pipe.expire(game_players_set, 1200)
    pipe.execute()
    return {"game_id": game_id, "player_id": player_id, "secret": secret}

@app.get("/")
@app.get("/hello")
async def hello():
    return {"message": "Hello World"}

@app.get("/games")
async def listGames(
        sortby: SortBy = SortBy.DATE,
        reverse: bool = False,
        start: int = 0, end: int = -1):

    if sortby == SortBy.DATE:
        if reverse:
            return r.zrange("games", start, end, withscores=True)
        return r.zrevrange("games", start, end, withscores=True)
    elif sortby == SortBy.NAME:
        if reverse:
            return r.zrevrangebylex("games", start, end, withscores=True)
        return r.zrangebylex("games", start, end, withscores=True)

@app.post("/create")
async def createGame(body: GameCreationInfo):
    return makeGame(body.dict())
