import asyncio
import discord
from discord.ext import commands
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext


class ChatTransport:
    def __init__(self):
        self.handlers = []

    def add_handler(self, event):
        self.handlers.append(event)

    async def send_message(self, msg):
        print(f"Sending message: {msg}")

    async def run(self):
        raise NotImplementedError("run method must be implemented in the subclass")


class ChatTransportDiscord(ChatTransport):
    def __init__(self, bot_token):
        super().__init__()
        intents = discord.Intents.all()
        self.bot = commands.Bot(command_prefix='!', intents=intents)
        self.token = bot_token

    async def send_message(self, msg):
        for handler in self.handlers:
            await handler(msg)

    async def run(self):
        @self.bot.event
        async def on_ready():
            print(f'Discord Bot logged in as {self.bot.user.name}')

        @self.bot.event
        async def on_message(message):
            await self.send_message(message.content)

        await self.bot.start(self.token)


class ChatTransportTelegram(ChatTransport):
    def __init__(self, bot_token):
        super().__init__()
        self.updater = Updater(bot_token, use_context=True)
        self.dp = self.updater.dispatcher

    async def send_message(self, msg):
        for handler in self.handlers:
            await handler(msg)

    async def run(self):
        def handle_telegram_message(update: Update, context: CallbackContext):
            msg = update.message.text
            asyncio.create_task(self.send_message(msg))

        message_handler = MessageHandler(Filters.text & ~Filters.command, handle_telegram_message)
        self.dp.add_handler(message_handler)

        self.updater.start_polling()
        self.updater.idle()


class SimpleBusinessLogicBot:
    def __init__(self, chat_transport):
        self.chat_transport = chat_transport
        self.chat_transport.add_handler(self.handle_message)

    async def handle_message(self, msg):
        response = f"Hi! Your message was received: {msg}"
        await self.chat_transport.send_message(response)

    async def start(self):
        await self.chat_transport.run()


discord_token = 'Discord Token'
discord_transport = ChatTransportDiscord(discord_token)
bot_discord = SimpleBusinessLogicBot(discord_transport)

telegram_token = 'Telegram Token'
telegram_transport = ChatTransportTelegram(telegram_token)
bot_telegram = SimpleBusinessLogicBot(telegram_transport)


async def run_bots():
    await asyncio.gather(
        bot_discord.start(),
        bot_telegram.start()
    )


asyncio.run(run_bots())
