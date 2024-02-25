import json
from string import ascii_uppercase
from typing import List, Tuple, Any

from core import send, read
from game.room import Room
from game.user import User
import random


class MsgType:
    LOGIN = 0
    LOGIN_ERROR = 1
    USER_JOIN = 2
    USER_LEFT = 3
    ERROR = 4
    ROOM_CREATED = 5
    ROOM_UPDATED = 6
    ROOM_DELETED = 7
    ROOM_JOINED = 8


class Action:
    LOGIN = 0
    NEW_ROOM = 1
    CHANGE_ROOM = 2


class ActionHandler:
    users: List[User]
    rooms: List[Room]
    actions: dict

    def __init__(self):
        self.users = []
        self.rooms = []
        self.actions = {
            1: self.action_create_room,
            2: self.action_change_room,
        }
        self.empty_room = Room('')
        self.empty_room.uuid = ''
        self.empty_room.users = self.users

    def add_user(self, user: User):
        self.users.append(user)

    def get_users(self):
        return self.users

    def remove_user(self, writer):
        for i in range(len(self.users)):
            if self.users[i].writer == writer:
                del self.users[i]
                return

    async def handle(self, user, action, data):
        print(user.uuid, action, data)
        await self.actions[action](user, data)

    async def login(self, reader, writer):
        end, data = await read(reader, writer)
        if end:
            return writer.close()
        message = data.decode('utf-8')
        try:
            payload = json.loads(message)
            if payload['action'] == Action.LOGIN and len(payload['data']['username']) > 0:
                user = User(writer, payload['data']['username'])
                self.add_user(user)
                print(f'New User: {user.username} on {writer.get_extra_info("peername")}')
                await send(
                    {
                        "self": user.get_broadcast(),
                        "users": [u.get_broadcast() for u in self.users],
                        "rooms": [r.get_broadcast() for r in self.rooms],
                    },
                    writer, mtype=MsgType.LOGIN)
                await send(user.get_broadcast(), writer, self.users, broadcast=True,
                           mtype=MsgType.USER_JOIN)
                return user
            await send("Wrong Credentials", writer, mtype=MsgType.LOGIN_ERROR)
            return writer.close()
        except Exception as e:
            print(e)
            return writer.close()

    async def action_create_room(self, user: User, data):
        name = '#' + ''.join(random.choices(ascii_uppercase, k=10))
        room = Room(name)
        self.rooms.append(room)
        self.remove_user(user.writer)
        room.join(user)

        await send({"users": [user.get_broadcast()], "rooms": [], "room": room.name}, user.writer, mtype=MsgType.ROOM_JOINED)
        await send(user.uuid, user.writer, self.users, broadcast=True, mtype=MsgType.USER_LEFT)
        await send(room.get_broadcast(), user.writer, self.users, broadcast=True, mtype=MsgType.ROOM_CREATED)
        await send(user.get_broadcast(), user.writer, room.users, broadcast=True, mtype=MsgType.USER_JOIN)

    async def action_change_room(self, user: User, data):
        try:
            old_room = self.empty_room
            new_room = self.empty_room
            for r in self.rooms:
                if r.uuid == data:
                    new_room = r
                if r.uuid == user.room:
                    old_room = r

            join = new_room.join(user)
            leave = old_room.leave(user)
            user.room = data
            rooms = []
            if new_room.uuid == '':
                rooms = [r.get_broadcast() for r in self.rooms]

            print(f'{join} {leave} New room {len(new_room.uuid)} {len(new_room.users)} Old room {len(old_room.uuid)} {len(old_room.users)}')

            await send(user.uuid, user.writer, old_room.users, broadcast=True, mtype=MsgType.USER_LEFT)
            await send(new_room.get_broadcast(), user.writer, old_room.users, broadcast=True, mtype=MsgType.ROOM_UPDATED)
            await send(old_room.get_broadcast(), user.writer, new_room.users, broadcast=True, mtype=MsgType.ROOM_UPDATED)
            await send({"users": [u.get_broadcast() for u in new_room.users], "rooms": rooms, "room": new_room.name}, user.writer, mtype=MsgType.ROOM_JOINED)
            await send(user.get_broadcast(), user.writer, new_room.users, broadcast=True, mtype=MsgType.USER_JOIN)
        except Exception as e:
            print(e)
