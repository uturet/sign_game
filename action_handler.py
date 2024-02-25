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

    def add_user(self, user: User):
        self.users.append(user)

    def get_users(self):
        return self.users

    def remove_user(self, writer, users=None):
        if users is None:
            users = self.users
        for i in range(len(users)):
            if users[i].writer == writer:
                del users[i]
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
            if payload['action'] == Action.LOGIN and len(payload['data']['username']) > 4:
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
        self.remove_user(user)
        room.join(user)

        await send({"users": [user.get_broadcast()], "room": room.uuid}, user.writer, mtype=MsgType.ROOM_JOINED)
        await send(user.uuid, user.writer, self.users, broadcast=True, mtype=MsgType.USER_LEFT)
        await send(room.get_broadcast(), user.writer, self.users, broadcast=True, mtype=MsgType.ROOM_CREATED)
        await send(user.get_broadcast(), user.writer, room.users, broadcast=True, mtype=MsgType.USER_JOIN)

    async def action_change_room(self, user: User, data):
        try:
            room_users = self.users
            prev_room_users = self.users
            room_id = ''
            for r in self.rooms:
                if r.uuid == data:
                    prev_room_users = r.users
                if r.uuid == data:
                    room_users = r.users
                    room_id = r.uuid

            self.remove_user(user.writer, users=prev_room_users)
            room_users.append(user)


            await send(user.uuid, user.writer, self.users, broadcast=True, mtype=MsgType.USER_LEFT)
            await send(user.uuid, user.writer, self.users, broadcast=True, mtype=MsgType.ROOM_UPDATED)
            await send({"users": [u.get_broadcast() for u in room_users], "room": room_id}, user.writer, mtype=MsgType.ROOM_JOINED)
            await send(user.get_broadcast(), user.writer, room_users, broadcast=True, mtype=MsgType.USER_JOIN)
        except Exception as e:
            print(e)
