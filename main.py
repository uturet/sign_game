import json

from action_handler import ActionHandler, Action, MsgType
from core import handshake, read, send
from game.user import User
from http import HTTPStatus
import asyncio.streams
import asyncio
import sys
import os

action_handler = ActionHandler()


async def get_response(writer, path):
    full_path = f'http/{path}'
    if not os.path.isfile(full_path):
        return
    with open(full_path, 'rb') as file:
        content = file.read()
        extension = path.split('.')[-1]
        if extension == 'js':
            extension = 'javascript'
        response = (
            f"HTTP/1.1 {HTTPStatus.OK}\r\n"
            f"Content-Type: text/{extension}\r\n"
            f"Content-Length: {len(content)}\r\n"
            "\r\n"
        )
        writer.write(response.encode('utf-8') + content)
        await writer.drain()


def parse_payload(data):
    data = data.decode('utf-8')
    try:
        data = json.loads(data)
        return True, data['action'], data['data']
    except Exception:
        return False, None, None


async def handle_client(reader, writer):
    await handshake(reader, writer, get_response)
    user = await action_handler.login(reader, writer)
    if user:
        await action_handler.remove_user(writer)
    if writer.is_closing():
        return await writer.wait_closed()

    while True:
        end, payload = await read(reader, writer)
        if end:
            break
        valid, action, data = parse_payload(payload)
        if not valid:
            await send("Invalid Data Format!", writer, mtype=MsgType.ERROR)
            continue
        action_handler.handle(action, data)

    print(f'User left: {user.username} on {writer.get_extra_info("peername")}')
    await send(user.uuid, writer, action_handler.get_users(), broadcast=True, mtype=MsgType.USER_LEFT)
    action_handler.remove_user(writer)
    writer.close()
    await writer.wait_closed()


async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', int(sys.argv[1]))
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
