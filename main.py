import json

from core import handshake, read, send
from game.user import User
from http import HTTPStatus
import asyncio.streams
import asyncio
import sys
import os
from typing import List

clients: List[User] = []


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


async def login(reader, writer):
    end, data = await read(reader, writer)
    if end:
        return writer.close()
    message = data.decode('utf-8')
    try:
        payload = json.loads(message)
        if payload['action'] == 'login' and len(payload['data']['username']) > 5:
            user = User(writer, payload['data']['username'])
            clients.append(user)
            print(f'New User: {user.username} on {writer.get_extra_info("peername")}')
            return
        await send({"type": "error", "message": "Wrong Credentials"}, writer, clients, broadcast=False)
        return writer.close()
    except Exception:
        return writer.close()


def remove_client(writer):
    for i in range(len(clients)):
        if clients[i].writer == writer:
            del clients[i]
            return


async def handle_client(reader, writer):
    address = writer.get_extra_info('peername')

    await handshake(reader, writer, get_response)
    await login(reader, writer)
    if writer.is_closing():
        remove_client(writer)
        return await writer.wait_closed()
    print(f"Accepted connection from {address}")

    while True:
        end, data = await read(reader, writer)
        if end:
            break
        message = data.decode('utf-8')
        print(f'Message from {address}: {message}')

        await send(message, writer, clients, broadcast=True)
        print('Sending Complete!')

    print(f"Connection with {address} closed.")
    await send(f"Connection with {address} closed.", writer, clients, broadcast=True)
    remove_client(writer)
    writer.close()
    await writer.wait_closed()


async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', int(sys.argv[1]))
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
