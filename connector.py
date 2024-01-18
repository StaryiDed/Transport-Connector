import asyncio
from abc import ABC, abstractmethod

class ChatTransport(ABC):
    def __init__(self):
        self.handlers = {}

    def add_handler(self, event, handler):
        self.handlers[event] = handler

    @abstractmethod
    async def send_message(self, msg):
        pass

    @abstractmethod
    async def run(self):
        pass

class ChatTransportDiscord(ChatTransport):
    def __init__(self, token, channel_id):
        super().__init__()
        import discord
        self.client = discord.Client()
        self.token = token
        self.channel_id = channel_id

        @self.client.event
        async def on_ready():
            print('Discord bot is ready.')

        @self.client.event
        async def on_message(message):
            if message.author == self.client.user or message.channel.id != self.channel_id:
                return
            if 'message' in self.handlers:
                await self.handlers['message'](message.content)

    async def send_message(self, msg):
        channel = self.client.get_channel(self.channel_id)
        if channel:
            await channel.send(msg)

    async def run(self):
        await self.client.start(self.token)

class ChatTransportTelegram(ChatTransport):
    def __init__(self, token):
        super().__init__()
        from telegram.ext import Updater, MessageHandler, Filters
        self.updater = Updater(token, use_context=True)

        def handle_message(update, context):
            if 'message' in self.handlers:
                asyncio.run(self.handlers['message'](update.message.text))

        self.updater.dispatcher.add_handler(MessageHandler(Filters.text, handle_message))

    async def send_message(self, msg):
        for chat_id in self.updater.dispatcher.chat_data.keys():
            self.updater.bot.send_message(chat_id, msg)

    async def run(self):
        self.updater.start_polling()
        await asyncio.Event().wait()
