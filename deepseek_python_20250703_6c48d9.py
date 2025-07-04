from telethon import TelegramClient, events
import asyncio
import logging

class TelegramMonitor:
    def __init__(self):
        self.client = None
        self.connected = False
        self.max_retries = 5
        self.retry_delay = 10
        
    async def connect(self):
        retries = 0
        while retries < self.max_retries:
            try:
                self.client = TelegramClient('session_name', api_id, api_hash)
                await self.client.start()
                self.connected = True
                logging.info("Successfully connected to Telegram")
                return True
            except Exception as e:
                retries += 1
                logging.error(f"Connection failed (attempt {retries}): {str(e)}")
                await asyncio.sleep(self.retry_delay)
        return False

    async def monitor_channels(self, channels):
        @self.client.on(events.NewMessage(chats=channels))
        async def handler(event):
            try:
                if event.message.photo:
                    text = await self.extract_text_from_image(event.message)
                else:
                    text = event.message.text
                await process_signal(text)
            except Exception as e:
                logging.error(f"Error processing message: {str(e)}")

        while True:
            if not self.connected:
                await self.connect()
            await asyncio.sleep(1)