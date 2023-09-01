import json
import os
import django
from decouple import config
os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'friend_trader.settings.{config("ENVIORNMENT")}')
django.setup()
from django.conf import settings
import asyncio
import websockets

from friend_trader_trader.models import Block
from friend_trader_dispatcher.tasks import perform_block_actions_task


class FriendTraderListener:
    blast_wss = f"wss://base-mainnet.blastapi.io/{settings.BLAST_WSS_API}"
    env = config("ENVIRONMENT")

    def sync_blocks(self):
        if self.env != "dev":
            blocks = list(Block.objects.order_by("block_number"))
            i = 0
            while i < len(blocks):
                curr_block = blocks[i]
                curr_block_num = curr_block.block_number
                next_block = blocks[i+1]
                if curr_block_num + 1 != next_block.block_number:
                    ...


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
    friend_trader.sync_blocks()
    asyncio.get_event_loop().run_until_complete(friend_trader.listen_for_new_blocks())


    

    
