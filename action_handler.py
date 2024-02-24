import json
from string import ascii_uppercase
from typing import List, Tuple, Any

from core import send, read
from game.room import Room
from game.user import User
import random


class MsgType:
    LOGIN = 0
    USER_JOIN = 1
    USER_LEFT = 2
    ERROR = 3


class Action:
    LOGIN = 0
    NEW_ROOM = 1
    CHANGE_ROOM = 2


class ActionHandler:
    users: List[User]
    rooms: List[Room]
    actions: Tuple[Any]

    def __init__(self, user):
        self.user = user
        self.users = []
        self.rooms = []
        self.actions = (
            self.action_create_room,
            self.action_change_room,
        )

    def add_user(self, user: User):
        self.users.append(user)

    def get_users(self):
        return self.users

    async def remove_user(self, writer):
        for i in range(len(self.users)):
            if self.users[i].writer == writer:
                await send(self.users[i].uuid, writer, self.users, broadcast=True, mtype=MsgType.USER_LEFT)
                del self.users[i]
                return

    def handle(self, action, data):
        self.actions[action](data)

    async def login(self, reader, writer):
        end, data = await read(reader, writer)
        if end:
            return writer.close()
        message = data.decode('utf-8')
        try:
            payload = json.loads(message)
            if payload['action'] == Action.LOGIN and len(payload['data']['username']) > 5:
                user = User(writer, payload['data']['username'])
                self.add_user(user)
                print(f'New User: {user.username} on {writer.get_extra_info("peername")}')
                await send(
                    {"self": user.get_broadcast(), "users": [u.get_broadcast() for u in self.users]},
                    writer, mtype=MsgType.LOGIN)
                await send(user.get_broadcast(), writer, self.users, broadcast=True,
                           mtype=MsgType.USER_JOIN)
                return user
            await send("Wrong Credentials", writer, mtype=MsgType.ERROR)
            return writer.close()
        except Exception:
            return writer.close()

    async def action_create_room(self, user: User, data):
        name = '#' + ''.join(random.choices(ascii_uppercase, k=10))
        room = Room(name)
        self.rooms.append(room)
        await self.remove_user(user)
        room.join(user)
        await send(user.get_broadcast(), user.writer, room.users, broadcast=True, mtype=MsgType.USER_JOIN)

    async def action_change_room(self, user: User, data):
        room_users = self.users
        prev_room_users = self.users
        for r in self.rooms:
            if r.uuid == user.room:
                prev_room_users = r.users
            if r.uuid == data:
                room_users = r.users

        await self.remove_user(prev_room_users)
        room_users.join(user)
        await send(user.get_broadcast(), user.writer, room_users, broadcast=True, mtype=MsgType.USER_JOIN)
