import disnake
import random
import asyncio
from disnake.ext import commands
from disnake import TextInputStyle

class UserExperience(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  def cog_load(self):
    print('Ког загружен: "{}"'.format(self.qualified_name))

  def cog_unload(self):
    print('Ког выгружен: "{}"'.format(self.qualified_name))

  @commands.Cog.listener()
  async def on_message(self, message):
    if message.author.bot or not message.guild: return
    if not str(message.author.id) in self.bot.db['members'].keys():
      print(f'Поймал сообщение от {message.author} - не в датабазе, игнорирую.')
    else:
      if (message.content.lower() == "а это цифра 9" or message.content.lower() == "а это цифра 9."):
          self.bot.add_user_to_db(message.author.id)
          if not self.bot.db['members'][str(message.author.id)]['achievements']['accessGranted']:
            embed = disnake.Embed(color=disnake.Color(0x474896))
            embed.description = 'Назвать кодовую фразу'
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/1017923933896441907/1101056017720160276/uz8BiFQ8vDI.jpg')
            embed.set_author(name=f'{message.author.display_name} получил(а) достижение "Доступ разрешён"', icon_url=message.author.display_avatar)
            await message.channel.send(embed=embed)
            await message.delete()
            self.bot.db['members'][str(message.author.id)]['achievements']['accessGranted'] = True
            print('Названа кодовая фраза!')
      else:
        if message.author.get_role(1061931684003577876):
          self.bot.db['members'][str(message.author.id)]['balance'] += random.randint(4,9)
          print(f'Поймал сообщение от {message.author} (Создатель актива)')
        elif message.author.get_role(1063012529640583179):
          self.bot.db['members'][str(message.author.id)]['balance'] += random.randint(3,7)
          print(f'Поймал сообщение от {message.author} (Ценитель общения)')
        elif message.author.get_role(1063012925591269426):
          self.bot.db['members'][str(message.author.id)]['balance'] += random.randint(2,5)
          print(f'Поймал сообщение от {message.author} (Словесная поддержка)')
        else:
          self.bot.db['members'][str(message.author.id)]['balance'] += random.randint(1,3)
          print(f'Поймал сообщение от {message.author}')

  @commands.slash_command(
    name='balance',
    description='Проверяет баланс участника',
    options=[
      disnake.Option('member', 'Участник, у которого вы хотите проверить баланс', disnake.OptionType.user, False),
    ])
  async def balance(self, inter: disnake.AppCmdInter, member: disnake.User = None):
    if member == None or member == inter.author:
      self.bot.add_user_to_db(inter.author.id)
      await inter.response.send_message('Ваш баланс: {0}<:kirieshka:1100873685201588285>'.format(self.bot.db['members'][str(inter.author.id)]['balance']),ephemeral=True)
      if not self.bot.db['members'][str(inter.author.id)]['achievements']['firstSteps'] and self.bot.db['members'][str(inter.author.id)]['balance'] >= 100:
        self.bot.db['members'][str(inter.author.id)]['achievements']['firstSteps'] = True
        embed = disnake.Embed(color=disnake.Color(0x474896))
        embed.description = 'Заработать первые 100 сухариков'
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/1017923933896441907/1100892814826549378/good.png')
        embed.set_author(name=f'{inter.author.display_name} получил(а) достижение "Первые шаги"', icon_url=inter.author.display_avatar)
        await inter.channel.send(embed=embed)
    else:
      if member.bot:
        await inter.response.send_message('Это бот, а не участник. Пожалуйста, выберите кого-нибудь поодушевлённее.',ephemeral=True)
      elif not str(member.id) in self.bot.db['members'].keys():
        await inter.response.send_message('Участника нет в датабазе. Как вы могли такое допустить?!',ephemeral=True)
      else:
        await inter.response.send_message('Баланс {1}: {0}<:kirieshka:1100873685201588285>'.format(self.bot.db['members'][str(member.id)]['balance'],member.display_name),ephemeral=True)
  @commands.user_command(name="Посмотреть баланс")
  async def ctx_balance(self, inter: disnake.AppCmdInter, member: disnake.User):
    if member == None or member == inter.author:
      self.bot.add_user_to_db(inter.author.id)
      await inter.response.send_message('Ваш баланс: {0}<:kirieshka:1100873685201588285>'.format(self.bot.db['members'][str(inter.author.id)]['balance']),ephemeral=True)
      if not self.bot.db['members'][str(inter.author.id)]['achievements']['firstSteps'] and self.bot.db['members'][str(inter.author.id)]['balance'] >= 100:
        self.bot.db['members'][str(inter.author.id)]['achievements']['firstSteps'] = True
        embed = disnake.Embed(color=disnake.Color(0x474896))
        embed.description = 'Заработать первые 100 сухариков'
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/1017923933896441907/1100892814826549378/good.png')
        embed.set_author(name=f'{inter.author.display_name} получил(а) достижение "Первые шаги"', icon_url=inter.author.display_avatar)
        await inter.channel.send(embed=embed)
    else:
      if member.bot:
        await inter.response.send_message('Это бот, а не участник. Пожалуйста, выберите кого-нибудь поодушевлённее.',ephemeral=True)
      elif not str(member.id) in self.bot.db['members'].keys():
        await inter.response.send_message('Участника нет в датабазе. Как вы могли такое допустить?!',ephemeral=True)
      else:
        await inter.response.send_message('Баланс {1}: {0}<:kirieshka:1100873685201588285>'.format(self.bot.db['members'][str(member.id)]['balance'],member.display_name),ephemeral=True)

  @commands.slash_command(
  name='embedcreate',
  description='Создаёт эмбед от вашего имени всего за 300 сухариков!')
  async def embedcreate(self, inter: disnake.AppCmdInter):
    if self.bot.db['members'][str(inter.author.id)]['balance'] < 300:
      await inter.response.send_message(content='Недостаточно средств для оплаты услуги! Возвращайтесь как заработаете нужную сумму.',ephemeral=True)
    else:
      await inter.response.send_modal(
        title="Создание эмбеда...",
        custom_id="embedcreate",
        components=[
          disnake.ui.TextInput(
            label="Заголовок",
            placeholder="Заголовок - он и в Африке заголовок",
            custom_id="title",
            style=TextInputStyle.paragraph,
            max_length=256,
            required=False
          ),
          disnake.ui.TextInput(
              label="Описание",
              placeholder="Внутренности эмбеда",
              custom_id="desc",
              style=TextInputStyle.paragraph,
              max_length=4000,
              required=False
          )
        ],
      )
      try:
        modal_inter: disnake.ModalInteraction = await self.bot.wait_for(
          "modal_submit",
          check=lambda i: i.custom_id == "embedcreate" and i.author.id == inter.author.id,
          timeout=300,
        )
      except asyncio.TimeoutError:
        return
    if not modal_inter.text_values['title'] and not modal_inter.text_values['desc']:
      await modal_inter.response.send_message('Толку от пустого сообщения, увы, немного. Создание отменено.',ephemeral=True)
    else:
      await modal_inter.response.defer(ephemeral=True)
      embed = disnake.Embed(color=disnake.Color(0x474896))
      embed.set_author(name=f'{inter.author.display_name} сказал:', icon_url=inter.author.display_avatar)
      embed.title = modal_inter.text_values['title']
      embed.description = modal_inter.text_values['desc']
      await modal_inter.channel.send(embed=embed)
      await modal_inter.edit_original_response('Эмбед отправлен!')
      self.bot.db['members'][str(inter.author.id)]['balance'] -= 300

  @commands.slash_command(
    name='achievements',
    description='Показывает ачивки участника',
    options=[
      disnake.Option('member', 'Участник, чьи ачивки вы хотите посмотреть', disnake.OptionType.user, False),
    ])
  async def achievements(self, inter: disnake.AppCmdInter, member: disnake.User = None):
    if member == None or member == inter.author:
      self.bot.add_user_to_db(inter.author.id)
      accessGranted = self.bot.db['members'][str(inter.author.id)]['achievements']['accessGranted']
      donator = self.bot.db['members'][str(inter.author.id)]['achievements']['donator']
      embed = disnake.Embed(color=disnake.Color(0x474896))
      embed.set_author(name=f'Достижения {inter.author.display_name}', icon_url=inter.author.display_avatar)
      embed.add_field(name='Первые шаги '+('✅' if self.bot.db['members'][str(inter.author.id)]['achievements']['firstSteps'] else '❌'),value='Заработать первые 100 сухариков', inline=False)
      embed.add_field(name='Дихлофос '+('✅' if self.bot.db['members'][str(inter.author.id)]['achievements']['bugHunter'] else '❌'),value='Сообщить об ошибке внутри бота',inline=False)
      embed.add_field(name='Доступ разрешён '+('✅' if accessGranted else '❌'),value='Назвать кодовую фразу'+('\n(бесполезная на первый взгляд фраза в правилах может помочь)' if not accessGranted else ''),inline=False)
      embed.add_field(name='Меценат '+(f'✅ (Пожертвовано {str(donator)}<:kirieshka:1100873685201588285>)' if donator>0 else '❌'),value='Принять участие в Цветном сборе'+('\n(можно хоть один сухарик, главное чтобы цель сбора была достигнута)' if donator==0 else ''),inline=False)
      await inter.response.send_message(embed=embed, ephemeral=True)
    else:
      if member.bot:
        await inter.response.send_message('Это бот, а не участник. Пожалуйста, выберите кого-нибудь поодушевлённее.',ephemeral=True)
      elif not str(member.id) in self.bot.db['members'].keys():
        await inter.response.send_message('Участника нет в датабазе. Как вы могли такое допустить?!',ephemeral=True)
      else:
        donator = self.bot.db['members'][str(member.id)]['achievements']['donator']
        embed = disnake.Embed(color=disnake.Color(0x474896))
        embed.set_author(name=f'Достижения {member.display_name}', icon_url=member.display_avatar)
        embed.add_field(name='Первые шаги '+('✅' if self.bot.db['members'][str(member.id)]['achievements']['firstSteps'] else '❌'),value='Заработать первые 100 сухариков', inline=False)
        embed.add_field(name='Дихлофос '+('✅' if self.bot.db['members'][str(member.id)]['achievements']['bugHunter'] else '❌'),value='Сообщить об ошибке внутри бота',inline=False)
        embed.add_field(name='Доступ разрешён '+('✅' if self.bot.db['members'][str(member.id)]['achievements']['accessGranted'] else '❌'),value='Назвать кодовую фразу',inline=False)
        embed.add_field(name='Меценат '+(f'✅ (Пожертвовано {str(donator)}<:kirieshka:1100873685201588285>)' if donator>0 else '❌'),value='Принять участие в Цветном сборе',inline=False)
        await inter.response.send_message(embed=embed, ephemeral=True)
  @commands.user_command(name="Глянуть достижения")
  async def ctx_achievements(self, inter: disnake.AppCmdInter, member: disnake.User):
    if member == inter.author:
      self.bot.add_user_to_db(inter.author.id)
      accessGranted = self.bot.db['members'][str(inter.author.id)]['achievements']['accessGranted']
      donator = self.bot.db['members'][str(inter.author.id)]['achievements']['donator']
      embed = disnake.Embed(color=disnake.Color(0x474896))
      embed.set_author(name=f'Достижения {inter.author.display_name}', icon_url=inter.author.display_avatar)
      embed.add_field(name='Первые шаги '+('✅' if self.bot.db['members'][str(inter.author.id)]['achievements']['firstSteps'] else '❌'),value='Воспользоваться ботом в первый раз', inline=False)
      embed.add_field(name='Дихлофос '+('✅' if self.bot.db['members'][str(inter.author.id)]['achievements']['bugHunter'] else '❌'),value='Сообщить об ошибке внутри бота',inline=False)
      embed.add_field(name='Доступ разрешён '+('✅' if accessGranted else '❌'),value='Назвать кодовую фразу'+('\n(бесполезная на первый взгляд фраза в правилах может помочь)' if not accessGranted else ''),inline=False)
      embed.add_field(name='Меценат '+(f'✅ (Пожертвовано {str(donator)}<:kirieshka:1100873685201588285>)' if donator>0 else '❌'),value='Принять участие в Цветном сборе'+('\n(можно хоть один сухарик, главное чтобы цель сбора была достигнута)' if donator==0 else ''),inline=False)
      await inter.response.send_message(embed=embed, ephemeral=True)
    else:
      if member.bot:
        await inter.response.send_message('Это бот, а не участник. Пожалуйста, выберите кого-нибудь поодушевлённее.',ephemeral=True)
      elif not str(member.id) in self.bot.db['members'].keys():
        await inter.response.send_message('Участника нет в датабазе. Как вы могли такое допустить?!',ephemeral=True)
      else:
        donator = self.bot.db['members'][str(member.id)]['achievements']['donator']
        embed = disnake.Embed(color=disnake.Color(0x474896))
        embed.set_author(name=f'Достижения {member.display_name}', icon_url=member.display_avatar)
        embed.add_field(name='Первые шаги '+('✅' if self.bot.db['members'][str(member.id)]['achievements']['firstSteps'] else '❌'),value='Воспользоваться ботом в первый раз', inline=False)
        embed.add_field(name='Дихлофос '+('✅' if self.bot.db['members'][str(member.id)]['achievements']['bugHunter'] else '❌'),value='Сообщить об ошибке внутри бота',inline=False)
        embed.add_field(name='Доступ разрешён '+('✅' if self.bot.db['members'][str(member.id)]['achievements']['accessGranted'] else '❌'),value='Назвать кодовую фразу',inline=False)
        embed.add_field(name='Меценат '+(f'✅ (Пожертвовано {str(donator)}<:kirieshka:1100873685201588285>)' if donator>0 else '❌'),value='Принять участие в Цветном сборе',inline=False)
        await inter.response.send_message(embed=embed, ephemeral=True)
  @commands.slash_command(name='balance_top', description='Топ-10 участников по балансу. Кому это вообще интересно?')
  async def bal_top(self, inter: disnake.AppCmdInter):
    k = 0
    desc=''
    output = {}
    for mid in self.bot.db["members"]:
      output[mid] = self.bot.db["members"][mid]["balance"]
    top = dict(sorted(output.items(), key=lambda x: x[1], reverse=True))
    for i in top:
      k+=1
      desc+='**'+str(k)+')** <@'+str(i)+'>: '+str(top[str(i)])+'<:kirieshka:1100873685201588285>\n'
      if k==10: break
    embed = disnake.Embed(description=desc, color=disnake.Color(0x474896))
    embed.set_author(name=f'Топ участников по балансу', icon_url='https://cdn.discordapp.com/attachments/1017923933896441907/1116426644530397334/93e1ccab15b8716a.png')
    await inter.response.send_message(embed=embed, ephemeral=True)

def setup(bot: commands.Bot):
  bot.add_cog(UserExperience(bot))