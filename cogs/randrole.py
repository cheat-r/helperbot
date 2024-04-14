from apscheduler.schedulers.asyncio import AsyncIOScheduler
import random
import time
import disnake
from disnake.ext import commands

class CogScheduler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()

    def cog_load(self):
        print('Ког загружен: "{}"'.format(self.qualified_name))

        self.scheduler.add_job(
            self.event_colorfunding_start,
            trigger='cron',
            hour='0',
            minute='0',
            second='0'
        )
        self.scheduler.add_job(
            self.event_colorfunding_end,
            trigger='cron',
            hour='23',
            minute='55',
            second='0'
        )
        self.scheduler.add_job(
            self.event_randrole,
            trigger='cron',
            hour='0',
            minute='0',
            second='0'
        )
        self.scheduler.add_job(
            self.event_db_clean,
            trigger='cron',
            day='1',
            hour='0',
            minute='0',
            second='0'
        )
        self.scheduler.add_job(
            self.event_customrole,
            trigger='cron',
            hour='3',
            minute='0',
            second='1'
        )

        self.scheduler.start()

    def cog_unload(self):
        print('Ког выгружен: "{}"'.format(self.qualified_name))
        self.scheduler.shutdown(False)

    async def event_colorfunding_start(self):
        print('Да начнётся же Цветной сбор! -> START')
        self.bot.db['colorFunding']['funded'] = False
        self.bot.db['colorFunding']['pledge'] = 0
        for user in self.bot.db['members']:
            self.bot.db['members'][user]['hold'] = 0

    async def event_customrole(self):
        guild = self.bot.get_guild(305031592068513796)
        for user in self.bot.db['members']:
            if self.bot.db['members'][user]['role']:
                if self.bot.db['members'][user]['role']['ts'] <= int(time.time()):
                    role = guild.get_role(self.bot.db['members'][user]['role']['id'])
                    if self.bot.db['members'][user]['role']['expired'] == True:
                        member = guild.get_member(int(user))
                        await role.delete()
                        self.bot.db['members'][user]['role']['id'] = 0
                        if member.dm_channel == None:
                            await member.create_dm()
                        await member.dm_channel.send(f'**Ваша кастом роль была удалена.**\nНе то, чтобы вы многое потеряли, просто теперь вам придётся пересоздавать её.\nТакие дела.')
                    else:
                        self.bot.db['members'][user]['role']['expired'] = True
                        self.bot.db['members'][user]['role']['ts'] += 259200
                        member = guild.get_member(int(user))
                        await member.remove_roles(role)
                        if member.dm_channel == None:
                            await member.create_dm()
                        await member.dm_channel.send(f'**Срок годности вашей кастом роли истёк...**\nЕсли вы не продлите её до <t:{self.bot.db["members"][user]["role"]["ts"]}:F>, она будет безвозвратно удалена и вам придётся создавать новую!\nВы ведь не хотите этого допустить?')

    async def event_colorfunding_end(self):
        print('Цветной сбор окончен. -> END')
        guild = self.bot.get_guild(305031592068513796)
        role = guild.get_role(1116112092290883704)
        self.bot.db['colorFunding']['funded'] = True
        if self.bot.db["colorFunding"]['pledge'] == 15000:
            await guild.create_role(name=str(role.color),color=role.color)
            for user in self.bot.db['members']:
                member = guild.get_member(int(user))
                if self.bot.db["members"][user]["hold"] > 0:
                    if member.dm_channel == None:
                        await member.create_dm()
                    channel = member.dm_channel
                    if self.bot.db['members'][user]['achievements']['donator'] == 0:
                        embed = disnake.Embed(color=disnake.Color(0x474896))
                        embed.description = 'Принять участие в Цветном сборе'
                        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/1013194723135062159/1152625250148831242/Niko_smile.webp')
                        embed.set_author(name=f'{member.display_name} получил(а) достижение "Меценат"', icon_url=member.display_avatar)
                        await channel.send(f"Спасибо за участие в Цветном сборе!\nМы смогли собрать нужную сумму и создали `{str(role.color)}`! Внесённые вами {self.bot.db['members'][user]['hold']}<:kirieshka:1100873685201588285> пошли на благое дело. (в вашу ачивку)\nЖдём вас на следующем сборе!",embed=embed)
                    else: await channel.send(f"Спасибо за участие в Цветном сборе!\nМы смогли собрать нужную сумму и создали `{str(role.color)}`! Внесённые вами {self.bot.db['members'][user]['hold']}<:kirieshka:1100873685201588285> пошли на благое дело. (в вашу ачивку)\nЖдём вас на следующем сборе!")
                    self.bot.db['members'][user]['achievements']['donator'] += self.bot.db['members'][user]['hold']
        else:
            for user in self.bot.db['members']:
                member = guild.get_member(int(user))
                if self.bot.db["members"][user]["hold"] > 0:
                    if member.dm_channel == None:
                        await member.create_dm()
                    channel = member.dm_channel
                    await channel.send(f"Спасибо за участие в Цветном сборе!\nК сожалению, нужная сумма не была собрана. Внесённые вами {self.bot.db['members'][user]['hold']}<:kirieshka:1100873685201588285> были возвращены на счёт.\nНадеемся, в следующий раз всё получится. Ждём вас на следующем сборе!")
                    self.bot.db['members'][user]['balance'] += self.bot.db['members'][user]['hold']            
    
    async def event_randrole(self):
        print('рандомить так рандомить, меняю цвет daily-роли')
        guild = self.bot.get_guild(305031592068513796)
        role = guild.get_role(1116112092290883704)
        color=int(''.join(random.choices('0123456789abcdef', k=6)), 16)
        await role.edit(color=disnake.Color(color), reason='новый день - новый цвет')

    async def event_db_clean(self):
        print('настала пора чистки...')
        guild = self.bot.get_guild(305031592068513796)
        for user in self.bot.db['members']:
            member = guild.get_member(int(user))
            if not self.bot.db['members'][user]['achievements']['firstSteps'] and not member.get_role(1014569986968268891):
                self.bot.db['members'][user].pop()

    @commands.slash_command(description='Цветной сбор! Очень интересная штука.', options=[
    disnake.Option('donate_value', 'Сумма пожертвования на сбор', disnake.OptionType.integer, min_value=1)])
    async def colorfunding(self, inter: disnake.ApplicationCommandInteraction, donate_value: int = None):
        guild = self.bot.get_guild(305031592068513796)
        role = guild.get_role(1116112092290883704)
        if donate_value:
            if self.bot.db['colorFunding']['funded'] == True:
                await inter.response.send_message('Сбор завершён. Ожидайте нового сбора. <:dafuq:1151801148714532895>', ephemeral=True)
                return
            if donate_value + self.bot.db['colorFunding']['pledge'] > 15000:
                donate_value = donate_value - (self.bot.db['colorFunding']['pledge'] + donate_value - 15000)
            if donate_value > self.bot.db['members'][str(inter.user.id)]['balance']:
                await inter.response.send_message('Недостаточно сухариков для пожертвования. Выберите сумму поменьше или идите работайте. <:nikotroll:1151984847334670388>', ephemeral=True)
            else:
                self.bot.db['members'][str(inter.user.id)]['balance'] -= donate_value
                self.bot.db['colorFunding']['pledge'] += donate_value
                self.bot.db['members'][str(inter.user.id)]['hold'] += donate_value
                if self.bot.db['colorFunding']['pledge'] == 15000:
                    self.bot.db['colorFunding']['funded'] = True
                    await inter.response.send_message('Спасибо за пожертвование.\nБлагодаря вам цель сбора была достигнута!', ephemeral=True)
                else:
                    left = 15000-self.bot.db['colorFunding']['pledge']
                    await inter.response.send_message(f'Спасибо за пожертвование.\nДо достижения цели сбора осталось `{left}`<:kirieshka:1100873685201588285>!', ephemeral=True)
        else:
            embed = disnake.Embed(title='Цветной сбор', description=f'Цель сбора: `{str(role.color)}` (<@&1116112092290883704>)')
            if self.bot.db['colorFunding']['funded']:
                if self.bot.db['colorFunding']['pledge'] == 15000:
                    embed.color=disnake.Color(0xfffffe)
                    embed.add_field(name='Собрано:', value=f'`15000`<:kirieshka:1100873685201588285> (Цель достигнута!)\n(Вы пожертвовали `{self.bot.db["members"][str(inter.user.id)]["hold"]}`<:kirieshka:1100873685201588285>)', inline=False)
                else:
                    embed.color=disnake.Color(0x000000)
                    embed.add_field(name='Собрано:', value=f'`{self.bot.db["colorFunding"]["pledge"]}`/`15000`<:kirieshka:1100873685201588285>\n(Вы пожертвовали `{self.bot.db["members"][str(inter.user.id)]["hold"]}`<:kirieshka:1100873685201588285>)', inline=False)
                ts=int(time.time()//86400*86400+161700)
                embed.add_field(name='Дедлайн:', value=f'(Завершён. Новый сбор начнётся <t:{ts}:R> <:nya:1017151159997321226>)')
            else:
                embed.color=role.color
                embed.add_field(name='Собрано:', value=f'`{self.bot.db["colorFunding"]["pledge"]}`/`15000`<:kirieshka:1100873685201588285>\n(Вы пожертвовали `{self.bot.db["members"][str(inter.user.id)]["hold"]}`<:kirieshka:1100873685201588285>)', inline=False)
                ts=int(time.time()//86400*86400+162000)
                embed.add_field(name='Дедлайн:', value=f'<t:{ts}:R>')
            await inter.response.send_message(embed=embed, ephemeral=True)

def setup(bot: commands.Bot):
    bot.add_cog(CogScheduler(bot))