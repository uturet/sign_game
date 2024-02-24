from game.game import Game
import uuid


class Room:

    OPEN = 0
    CLOSED = 1

    game: Game

    def __init__(self, name):
        self.name = name
        self.stage = self.OPEN
        self.uuid = str(uuid.uuid4())
        self.users = []

    def join(self, user):
        self.users.append(user)
        user.room = self.uuid

    def close(self):
        if all([u.is_ready for u in self.users]):
            self.stage = self.CLOSED
            self.game = Game(self.users)
            return True
        return False

    def add_user(self, user):
        self.users.append(user)

    def remove_user(self, user):
        self.users.remove(user)

    def get_game(self):
        return self.game

    def get_broadcast(self):
        return {
            'usersCount': len(self.users),
            'name': self.name,
            'uuid': self.uuid
        }
