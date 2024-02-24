from user import User
import random


class Game:

    STAGE_SHUFFLE = 0
    STAGE_RUN = 1
    STAGE_CATCH = 2

    catcher: User
    flag_holder: User
    score = 0

    signs = [i for i in range(20)]

    def __init__(self, players):
        self.players = players
        self.stage = self.STAGE_SHUFFLE

    def shuffle(self):
        flag_holder_index = random.randint(0, len(self.players)-1)
        self.flag_holder = self.players[flag_holder_index]
        self.flag_holder.has_flag = True

        players = self.players[:flag_holder_index] + self.players[flag_holder_index:]
        self.catcher = players[random.randint(0, len(self.players) - 1)]
        self.catcher.is_alive = True

        player_signs = []
        while len(player_signs) < len(self.players):
            sign = random.choice(self.signs)
            if sign not in player_signs:
                player_signs.append(sign)
        for i, sign in enumerate(player_signs):
            self.players[i].set_sign(sign)

    def set_flag_holder(self, user):
        self.score += 1
        self.flag_holder.has_flag = False
        self.flag_holder = user
        self.flag_holder.has_flag = True

    def next_stage(self):
        if self.stage == self.STAGE_SHUFFLE:
            self.stage = self.STAGE_RUN
        elif self.stage == self.STAGE_RUN:
            self.stage = self.STAGE_CATCH

