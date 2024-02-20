import asyncio.streams
import asyncio
import base64
import hashlib
import socket
import struct
import sys

clients = []


async def read(reader, writer):
    try:
        header = await reader.read(2)
    except asyncio.CancelledError:
        return True, b''  # Gracefully handle cancellation
    except ConnectionResetError:
        return True, b''  # Handle disconnection
    opcode = header[0] & 0xF
    payload_length = header[1] & 0x7F

    if payload_length == 126:
        payload_length = struct.unpack("!H", await reader.read(2))[0]
    elif payload_length == 127:
        payload_length = struct.unpack("!Q", await reader.read(8))[0]

    mask = await reader.read(4)
    data = await reader.read(payload_length)

    decoded_data = bytearray([data[i] ^ mask[i % 4] for i in range(payload_length)])

    if opcode == 8:  # Connection close
        return True, decoded_data

    if opcode == 1:  # Text frame
        return False, decoded_data

    # Echo the received data back to the client
    await writer.sendall(data)
    writer.write(data)
    await writer.drain()
    return False, decoded_data


def generate_websocket_accept_key(client_key):
    websocket_guid = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    combined_key = client_key + websocket_guid
    sha1_hash = hashlib.sha1(combined_key.encode('utf-8')).digest()
    websocket_accept_key = base64.b64encode(sha1_hash).decode('utf-8')
    return websocket_accept_key


async def handshake(reader, writer):
    print(f'Handshake {writer.get_extra_info("peername")}')
    try:
        request = await asyncio.wait_for(reader.readuntil(b'\r\n\r\n'), timeout=1)
    except asyncio.TimeoutError:
        print("Handshake timeout")
        return
    request = request.decode('utf-8')
    headers = request.split('\r\n')
    for header in headers:
        if "Sec-WebSocket-Key" in header:
            client_key = header.split(': ')[1]
            websocket_accept_key = generate_websocket_accept_key(client_key)
            response = (
                "HTTP/1.1 101 Switching Protocols\r\n"
                "Upgrade: websocket\r\n"
                "Connection: Upgrade\r\n"
                f"Sec-WebSocket-Accept: {websocket_accept_key}\r\n\r\n"
            )
            writer.write(response.encode('utf-8'))
            await writer.drain()
            break


async def broadcast(message: str | bytes, writer):
    if type(message) is str:
        data = message.encode('utf-8')
    else:
        data = message

    opcode = 0x1
    fin = 0x1

    # Split the data into chunks with a maximum size of 125 bytes
    chunk_size = 125
    chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

    for i, chunk in enumerate(chunks):
        # Set fin for the last frame
        fin = 0x1 if i == len(chunks) - 1 else 0x0

        # Opcode 0x0 for continuation frames if it's not the first frame
        opcode = 0x1 if i == 0 else 0x0

        header = struct.pack("!B", (fin << 7) | opcode)

        if len(chunk) <= 125:
            header += struct.pack("!B", len(chunk))
        elif 126 <= len(chunk) <= 65535:
            header += struct.pack("!BH", 126, len(chunk))
        else:
            header += struct.pack("!BQ", 127, len(chunk))

        for client in clients:
            # if client != writer:
            if True:
                print(f'Sending to {writer.get_extra_info("peername")}: {message}')
                try:
                    client.write(header + chunk)
                    await client.drain()
                except asyncio.CancelledError:
                    print("Cancelled")


async def handle_client(reader, writer):
    address = writer.get_extra_info('peername')
    clients.append(writer)

    print(f"Accepted connection from {address}")

    await handshake(reader, writer)
    # await broadcast(f"Accepted connection from {address}", writer)

    while True:
        end, data = await read(reader, writer)
        if end:
            break
        message = data.decode('utf-8')
        print(f'Message from {address}: {message}')

        await broadcast(message + ' Thank you for connection!', writer)
        print('Sending Complete!')

    print(f"Connection with {address} closed.")
    await broadcast(f"Connection with {address} closed.", writer)
    clients.remove(writer)
    writer.close()
    await writer.wait_closed()


async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', int(sys.argv[1]))

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
