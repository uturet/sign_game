from game.sign import Sign


class User:

    username: str
    room: str
    is_catcher: bool = False
    has_flag: bool = False
    is_ready: bool = False
    sign: Sign

    def __init__(self, writer, username):
        self.writer = writer
        self.username = username

    def set_room(self, room_name):
        self.room = room_name

    def set_is_catcher(self, is_catcher):
        self.is_catcher = is_catcher

    def set_has_flag(self, has_flag):
        self.has_flag = has_flag

    def set_is_ready(self, is_ready):
        self.is_ready = is_ready

    def set_sign(self, sign):
        self.sign = sign

