import os
import json
import disnake
from datetime import datetime
from disnake.ext import commands
from disnake.ext import tasks

class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        with open('db.json', 'r', encoding='utf-8') as fp:
            self.db = json.load(fp)
        self.start_time = datetime.now()
        self.task_autosave.start()
        super().__init__(
            command_prefix="!",
            help_command=None,
            intents=disnake.Intents.all(),
            status=disnake.Status.idle,
            activity=disnake.CustomActivity(state="[Редизайн!!!]", name='Custom Status'),
            reload=True,
            *args,
            **kwargs
        )

    @tasks.loop(minutes=10.0)
    async def task_autosave(self):
        await self.db_autosave()

    @task_autosave.before_loop
    async def task_autosave_before(self):
        await self.wait_until_ready()

    async def db_autosave(self):
        print('Автосохранение - сохраняем данные в JSON...')
        with open('db.json', 'w', encoding='utf-8') as fp:
            json.dump(self.db, fp, indent=2, ensure_ascii=False)    

    async def db_save(self):
        print('Сохраняем данные в JSON...')
        with open('db.json', 'w', encoding='utf-8') as fp:
            json.dump(self.db, fp, indent=2, ensure_ascii=False)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.bot: return
        if str(member.id) in self.db['members'].keys():
            if not self.db['members'][str(member.id)]['achievements']['firstSteps']:
                self.db['members'].pop(str(member.id))
                self.db_save()

    def add_user_to_db(self, user_id: int):
        if not str(user_id) in self.db['members'].keys():
            self.db['members'][str(user_id)] = {
                "balance": 0,
                "hold": 0,
                "achievements": {
                "firstSteps": False,
                "bugHunter": False,
                "accessGranted": False,
                "donator": 0
                },
                "inventory": {}
            }

bot = Bot()

@bot.event
async def on_ready():
    print(f"Залогинились как {bot.user} (ID: {bot.user.id})\n------")

@bot.command()
@commands.is_owner()
async def cogload(ctx, extension):
    bot.load_extension(f'cogs.{extension}')
    await ctx.message.delete()

@bot.command()
@commands.is_owner()
async def cogunload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    await ctx.message.delete()

@bot.command()
@commands.is_owner()
async def cogreload(ctx, extension):
    bot.reload_extension(f'cogs.{extension}')
    await ctx.message.delete()

for filename in os.listdir('cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

token = open('token-do-not-steal-you-piece-of-shit.txt', 'r').readline()
bot.run(token)