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
    async def ping(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.send_message(f"Понг! {round(self.bot.latency * 1000)}мс", ephemeral=True)
    
    @commands.slash_command(description='Базовая информация о боте')
    async def help(self, inter: disnake.ApplicationCommandInteraction):
        embed = disnake.Embed(title='Основные сведения о боте', color=disnake.Color(0x474896))
        embed.add_field(name='⚙️ Механики',value='Сухарики, или Кириешки, или <:kirieshka:1100873685201588285> - основная валюта внутри сервера и бота.\nИх можно тратить на всякое разное.\nЗа каждое сообщение по умолчанию начисляется 1-3 сухариков. Заработок можно увеличить, получив [медали за активность](https://discord.com/channels/305031592068513796/1187134858531713075/1187135112463253515). Бронза даёт 2-5, серебро 3-7, золото 4-9.\nДа, функионал не такой большой, но он потихоньку расширяется. Если есть желание помочь, отправляйте фидбек <@303930559976046603> на сервер или в ЛС, или напрямую почините что-нибудь [~~в говнокоде~~ на ГитХабе](https://github.com/cheat-r/helperbot), если вы поймёте что там написано.',inline=False)
        embed.add_field(name='💵 Экономика',value='`/balance` - проверяет баланс участника\n`/balance_top` - топ-10 участников по балансу на сервере\n`/inventory` - инвентарь с вашими купленными или выданными безделушками, где их можно использовать\n`/shop` - магазин всяких безделушек, от кастомной роли до банки пива',inline=False)
        embed.add_field(name='ℹ️ Полезное',value='`/embedcreate` - отправляет эмбед от лица бота за 300 сухариков (с заголовком и описанием)\n`/help` - вы здесь!\n`/ping` - пинг от бота до серверов Дискорда без излишних изысков в виде оформления сообщения. Для тех, кому по какой-то причине не нравится смотреть всю статистику сразу.\n`/statistics` - сведения о боте: аптайм, пинг, нагрузка на ОЗУ и процессор',inline=False)
        embed.add_field(name='🥳 Развлекалово',value='`/achievements` - всякие интересные достижения внутри сервера\n`/colorfunding` - ежедневный краудфандинг для сбора сухариков на создание новых цветов в <id:customize>\n`/duel` - как Buckshot Roulette, только называется Револьветка (Revolvette). Зачем? ||По приколу.||\n`/emoji` - отправляет любой эмодзи от лица бота, в том числе анимированный',inline=False)
        await inter.response.send_message(embed=embed, ephemeral=True)    
    @commands.Cog.listener()
    async def on_message(self, message):
      if message.author.bot: return
      if self.bot.user.mention == message.content:
        await message.reply('Привет! \nЕсли понадоблюсь, я в слеш-командах. (или используй `/help`, если хочешь узнать обо мне подробнее)')

    @commands.slash_command(description='Полезная (и не очень) статистика, на случай если вам интересно')
    async def statistics(self, inter: disnake.ApplicationCommandInteraction):
      uptime = datetime.now().timestamp() - self.bot.start_time.timestamp()
      time_d = int(uptime) / (3600 * 24)
      time_h = int(uptime) / 3600 - int(time_d) * 24
      time_min = int(uptime) / 60 - int(time_h) * 60 - int(time_d) * 24 * 60
      time_sec = int(uptime) - int(time_min) * 60 - int(time_h) * 3600 - int(time_d) * 24 * 60 * 60
      uptime_str = '%01d дн., %02d ч., %02d мин. и %02d сек.' % (time_d, time_h, time_min, time_sec)
      process = psutil.Process(os.getpid())
      cpu_percent = psutil.cpu_percent()
      ram = psutil.virtual_memory()
      ram_used = human_readable_size(ram.used)
      ram_total = human_readable_size(ram.total)
      ram_available = human_readable_size(ram.available)
      embed = disnake.Embed(title=':information_source: Статистика бота', color=disnake.Color(0x474896))
      embed.add_field(name=':clock1: Аптайм бота',value=f'{uptime_str} (<t:{int(self.bot.start_time.timestamp())}:R>)',inline=False)
      embed.add_field(name=':control_knobs: Расход процессора',value=f'{cpu_percent}%',inline=True)
      embed.add_field(name=':file_cabinet: Расход ОЗУ',value=human_readable_size(process.memory_info().rss),inline=True)
      embed.add_field(name=':file_cabinet: Всего ОЗУ',value=f'Занято: {ram_used} ({ram.percent}%) / {ram_total}\nСвободно: {ram_available} ({ram.available * 100 / ram.total:.1f}%)',inline=False)
      embed.add_field(name=':signal_strength: Пинг',value=f'{round(self.bot.latency * 1000)}мс',inline=True)
      await inter.response.send_message(embed=embed, ephemeral=True)
      
def setup(bot: commands.Bot):
    bot.add_cog(Help(bot))