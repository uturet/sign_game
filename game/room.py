from game import Game


class Room:

    OPEN = 0
    CLOSED = 1

    game: Game

    def __init__(self, name, users):
        self.name = name
        self.users = users
        self.stage = self.OPEN

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
