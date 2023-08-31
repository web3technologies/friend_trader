import json
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'friend_trader.settings.settings')
django.setup()
from django.conf import settings
import asyncio
import websockets
from friend_trader_dispatcher.tasks import perform_block_actions_task


class FriendTraderListener:
    blast_wss = f"wss://base-mainnet.blastapi.io/{settings.BLAST_WSS_API}"

    async def handle_connection(self):
        
        async with websockets.connect(self.blast_wss) as ws:
            await ws.send(json.dumps({
                "id": 1,
                "jsonrpc": "2.0",
                "method": "eth_subscribe",
                "params": ["newHeads"]
                }
            ))
            message = await ws.recv()
            while True:
                message = await ws.recv()
                block_hash = json.loads(message).get('params').get('result').get("hash")
                print(block_hash)
                perform_block_actions_task.delay(block_hash)
                
    async def listen_for_new_blocks(self):
        try:      
            await self.handle_connection()
        except (websockets.ConnectionClosed, websockets.ConnectionClosedError):
            print("Connection lost. Reconnecting...")
            await self.handle_connection()
        except Exception as e:
            print(f"Error: {e}")
        

if __name__ == "__main__":
    friend_trader = FriendTraderListener()
    asyncio.get_event_loop().run_until_complete(friend_trader.listen_for_new_blocks())


    

    
