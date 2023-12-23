import os
import psutil
from datetime import datetime
from utils import human_readable_size
import disnake
from disnake.ext import commands

class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot  

    def cog_load(self):
        print('Ког загружен: "{}"'.format(self.qualified_name))

    def cog_unload(self):
        print('Ког выгружен: "{}"'.format(self.qualified_name))

    @commands.slash_command(description='Пинает бота и отображает пинг')
    async def ping(self, inter: disnake.ApplicationCommandInteraction ):
        await inter.response.send_message(f"Понг! {round(self.bot.latency * 1000)}мс", ephemeral=True)
    
    @commands.slash_command(description='Базовая информация о боте')
    async def help(self, inter: disnake.ApplicationCommandInteraction ):
        await inter.response.send_message('хелпер - это бот с экономикой, в которой валюта (сухарики/кириешки/<:kirieshka:1100873685201588285>) зарабатывается живым общением в чате и участием в ивентах. \nсухарики можно тратить на всякие штуки в магазине, типа кастом роли или пива. \nа ещё есть достижения, которые ничего не дают, но зато отображаются у вас в профиле. \n\nфункционала не очень много, поэтому обратный фидбек нам очень важен. если у вас есть хорошая идея для предмета/ачивки/будь-чего-ещё, не стесняйтесь рассказывать о ней! авторов лучших идей мы будем награждать. \nна этом пока всё. если я понадоблюсь, я всегда буду в меню слеш-команд.',ephemeral=True)
    
    @commands.Cog.listener()
    async def on_message(self, message):
      if message.author.bot: return
      if self.bot.user.mention == message.content:
        await message.reply('Привет! \nЕсли понадоблюсь, я в слеш-командах. (или используй </help:1147182522283855964>, если хочешь узнать обо мне подробнее)')

    @commands.slash_command(description='Полезная (и не очень) статистика, на случай если вам интересно')
    async def statistics(self, inter: disnake.ApplicationCommandInteraction):
      uptime = datetime.now().timestamp() - self.bot.start_time.timestamp()
      time_d = int(uptime) / (3600 * 24)
      time_h = int(uptime) / 3600 - int(time_d) * 24
      time_min = int(uptime) / 60 - int(time_h) * 60 - int(time_d) * 24 * 60
      time_sec = int(uptime) - int(time_min) * 60 - int(time_h) * 3600 - int(time_d) * 24 * 60 * 60
      uptime_str = '%01d дн., %02d ч., %02d мин. и %02d сек.' % (time_d, time_h, time_min, time_sec)
      cpu_percent = psutil.cpu_percent()
      ram = psutil.virtual_memory()
      ram_used = human_readable_size(ram.used)
      ram_total = human_readable_size(ram.total)
      ram_available = human_readable_size(ram.available)
      embed = disnake.Embed(title=':information_source: Статистика бота', color=disnake.Color(0x474896))
      embed.add_field(name=':clock1: Аптайм бота',value=f'{uptime_str} (<t:{int(self.bot.start_time.timestamp())}:R>)',inline=False)
      embed.add_field(name=':control_knobs: Использование процессора',value=f'{cpu_percent}%',inline=True)
      embed.add_field(name=':file_cabinet: Использование ОЗУ',value=human_readable_size(process.memory_info().rss),inline=True)
      embed.add_field(name=':file_cabinet: Всего ОЗУ',value=f'Using: {ram_used} ({ram.percent}%) / {ram_total}\nAvailable: {ram_available} ({ram.available * 100 / ram.total:.1f}%)',inline=False)
      embed.add_field(name=':signal_strength: Пинг',value=f'{round(self.bot.latency * 1000)}ms',inline=True)
      await inter.response.send_message(embed=embed, ephemeral=True)
      
def setup(bot: commands.Bot):
    bot.add_cog(Help(bot))