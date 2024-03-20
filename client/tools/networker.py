import aiohttp
import requests
import asyncio
import json
import websockets

class MessengerClient:
    def __init__(self, base_url):
        self.base_url = "http://" + base_url
        self.headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }


    async def fetch(self, url, method='GET', data=None):
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, data=data) as response:
                return await response.json()

    async def get_server_data(self):
        url = f'{self.base_url}/'
        return await self.fetch(url)

    def find_user(self, user_name):
        url = f'{self.base_url}/find_user/{user_name}'
        return requests.get(url, headers={'accept': 'application/json'}).json()

    def send_invites(self, invites_data):
        url = f'{self.base_url}/send_invites'
        return requests.post(url, json=invites_data, headers=self.headers).json()

    async def get_new_invites(self, from_user):
        url = f'{self.base_url}/new_invites/{from_user}'
        return await self.fetch(url)

    def register(self, registration_data):
        url = f'{self.base_url}/register'
        return requests.post(url, json=registration_data, headers=self.headers).json()

    def send_message(self, message_data):
        url = f'{self.base_url}/send_message'

        return requests.post(url, json=message_data, headers=self.headers)

    async def ws_handler(self, user_id):
        async with websockets.connect(f'ws://localhost:8000/ws/{user_id}') as websocket:
            while True:
                try:
                    data = await websocket.recv()
                    yield json.loads(data)
                except websockets.exceptions.ConnectionClosedError:
                    print(f"Connection closed for user_id: {user_id}")


