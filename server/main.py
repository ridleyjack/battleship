from fastapi import FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from battleship import Battleship, Ship, Cell, NotPlayersTurn, AlreadyShot, OutOfBounds, GameOver


import os


app = FastAPI()
game = Battleship()

allowedOrigins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowedOrigins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ShotRequest(BaseModel):
    player: int = Field(strict=True, ge=0, le=1)
    x: int = Field(strict=True, ge=0)
    y: int = Field(strict=True, ge=0)

def serialize_board(board, showShips):
    result = []
    for row in board:
        output = []
        for col in row:
            if col == Cell.MISS:
                val = "M"
            elif col == Cell.HIT:
                val = "X"
            elif showShips and isinstance(col, Ship):
                val = "S"
            else:
                val = "O"
            output.append(val)
        result.append(output)
    return result

def print_serialized_board(board):
    for row in board:
        for col in row:
            print("", col, "", end="")
        print("")

@app.get("/")
def read_root():
    return {"message" : "Welcome to Battleship!"}

@app.get("/game/{player}")
def get_game(player: int = Path(ge=0, le=1)):
    p = game.get_player(player)

    if player == 0:
        targetBoard = game.get_player(1).board
    else:
        targetBoard = game.get_player(0).board

    return {
        "shipsAlive": p.shipsAlive,
        "ownBoard": serialize_board(p.board, True),
        "targetBoard": serialize_board(targetBoard, False),
        "gameOver": game.game_over()
    }

@app.post("/shoot")
def shoot(request: ShotRequest):
    try:
        result = game.shoot(
            request.player,
            request.x,
            request.y
        )
    except (GameOver, NotPlayersTurn, AlreadyShot) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except(OutOfBounds) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return {
        "result": result,
        "gameOver": game.game_over()
    }


@app.post("/reset")
def reset():
    global game
    game = Battleship()
