from fastapi import FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware

from battleship import Battleship, Ship, Cell
from pydantic import BaseModel, Field

app = FastAPI()
game = Battleship()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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
    targetPlayerID = 1 - request.player
    target = game.get_player(targetPlayerID)
    board = target.board

    if request.y >= len(board):
        raise HTTPException(422, detail="Row is outside the board.")

    if request.x >= len(board[request.y]):
        raise HTTPException(422, detail="Column is outside the board.")

    if game.game_over():
        raise HTTPException(409, detail="Game is over. Reset to play again.")

    if board[request.y][request.x] in (Cell.HIT, Cell.MISS):
        raise HTTPException(409, detail="You already fired at this tile.")

    result = game.shootAt(
        targetPlayerID,
        request.x,
        request.y
    )

    return {
        "result": result,
        "gameOver": game.game_over()
    }


@app.post("/reset")
def reset():
    global game
    game = Battleship()
