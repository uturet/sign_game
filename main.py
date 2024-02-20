from core import handshake, read, broadcast
from http import HTTPStatus
import asyncio.streams
import asyncio
import sys
import os

clients = []


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


async def handle_client(reader, writer):
    address = writer.get_extra_info('peername')
    clients.append(writer)

    await handshake(reader, writer, get_response)
    if writer.is_closing():
        clients.remove(writer)
        return await writer.wait_closed()
    print(f"Accepted connection from {address}")

    while True:
        end, data = await read(reader, writer)
        if end:
            break
        message = data.decode('utf-8')
        print(f'Message from {address}: {message}')

        await broadcast(message + ' Thank you for connection!', writer, clients)
        print('Sending Complete!')

    print(f"Connection with {address} closed.")
    await broadcast(f"Connection with {address} closed.", writer, clients)
    clients.remove(writer)
    writer.close()
    await writer.wait_closed()


async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', int(sys.argv[1]))
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
