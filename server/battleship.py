import random

from enum import Enum, auto


class NotPlayersTurn(Exception):
    pass
class AlreadyShot(Exception):
    pass
class OutOfBounds(Exception):
    pass
class GameOver(Exception):
    pass

class Cell(Enum):
    EMPTY = auto()
    MISS = auto()
    HIT = auto()

class Ship:
    def __init__(self, name, health):
        self.name = name
        self.health = health
    
    def hit(self):
        self.health = self.health -1

    def dead(self):
        return self.health <= 0

    def name(self):
        return self.name

class Player:
    def __init__(self, boardWidth, boardHeight):
        self.ships = [Ship("Carrier", 5), Ship("Battleship", 4), Ship("Cruiser", 3), Ship("Submarine", 3), Ship("Destroyer", 2)]
        self.shipsAlive = len(self.ships)

        self.board = [[Cell.EMPTY for _ in range(boardWidth)] for _ in range(boardHeight)]
        for ship in self.ships:
            placed = False
            while placed == False:
                horiz = random.randint(0, 1)
                x = random.randint(0, boardWidth-1)
                y = random.randint(0, boardHeight-1)

                fits = True
                x2 = x
                y2 = y
                for _ in range(ship.health):
                    if x2 >= boardWidth or y2 >= boardHeight or self.board[y2][x2] != Cell.EMPTY:
                        fits = False
                        break
                    if horiz:
                        x2 = x2+1
                    else:
                        y2 = y2+1
                if not fits:
                    continue

                x2 = x
                y2 = y
                for _ in range(ship.health):
                    self.board[y2][x2] = ship
                    if horiz:
                        x2 = x2+1
                    else:
                        y2 = y2+1
                placed = True

    def validate_shot(self, x, y):
        if y < 0 or y >= len(self.board):
            raise OutOfBounds("Shot row is out of bounds!") 
        if x < 0 or x >= len(self.board[0]):
            raise OutOfBounds("Shot column is out of bounds!") 
        cell = self.board[y][x]
        if cell == Cell.MISS or cell == Cell.HIT:
            raise AlreadyShot("You have already shot at this tile!")

    def shoot(self, x, y):
        self.validate_shot(x, y)
        cell = self.board[y][x]

        if cell == Cell.EMPTY:
            self.board[y][x] = Cell.MISS
            return "Miss!"

        # Otherwise it's a ship
        ship = cell
        self.board[y][x] = Cell.HIT        
        ship.health = ship.health - 1
        if ship.dead():
            self.shipsAlive -= 1
            return ship.name + " sunk!"
        
        return "Hit!"


class Battleship:
    def __init__(self):
        width = 10
        height = 10

        self.playerTurn = 0        
        self.playerA = Player(width, height)
        self.playerB = Player(width, height)

    def shoot(self, player, x, y):
        if self.game_over():
            raise GameOver("Game is over!")
        if player != self.playerTurn:
            raise NotPlayersTurn("It's not your turn!")

        target = self.get_player(1 - player)
        result = target.shoot(x, y)

        # Above throws on invalid shot.
        self.playerTurn = 1 - self.playerTurn
        return result

    def game_over(self):
        return self.playerA.shipsAlive == 0 or self.playerB.shipsAlive == 0

    def get_player(self, player):
        if player == 0:
            return self.playerA
        return self.playerB
