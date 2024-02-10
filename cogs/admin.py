import disnake
from disnake.ext import commands

class Admin(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  def cog_load(self):
    print('Ког загружен: "{}"'.format(self.qualified_name))

  def cog_unload(self):
    print('Ког выгружен: "{}"'.format(self.qualified_name))

  @commands.slash_command(
    name='balance_edit',
    description='Изменяет (точнее заменяет) баланс участника',
    options=[
      disnake.Option('member', 'Участник, которому вы хотите изменить баланс', disnake.OptionType.user, True),
      disnake.Option('amount', 'На какое значение заменить баланс', disnake.OptionType.integer, True, min_value=0)
    ])
  @commands.default_member_permissions(administrator=True)
  async def bal_edit(self, inter: disnake.AppCmdInter, member: disnake.User, amount: int):
    if member.bot:
      await inter.response.send_message('Это бот, а не участник. Пожалуйста, выберите кого-нибудь поодушевлённее.',ephemeral=True)
    elif not str(member.id) in self.bot.db['members'].keys():
      await inter.response.send_message('Участника нет в датабазе. Как вы могли такое допустить?!', ephemeral=True)
    else:
      self.bot.db['members'][str(member.id)]['balance'] = amount
      await inter.response.send_message('Баланс изменён.', ephemeral=True)

  @commands.slash_command(
    name='balance_give',
    description='Выдаёт (или отнимает) сухарики на счёт участника',
    options=[
      disnake.Option('member', 'Участник, которому вы хотите изменить баланс', disnake.OptionType.user, True),
      disnake.Option('amount', 'Сколько выдать (отрицательное число если отнять)', disnake.OptionType.integer, True)
    ])
  @commands.default_member_permissions(administrator=True)
  async def bal_give(self, inter: disnake.AppCmdInter, member: disnake.User, amount: int):
    if member.bot:
      await inter.response.send_message('Это бот, а не участник. Пожалуйста, выберите кого-нибудь поодушевлённее.',ephemeral=True)
    elif not str(member.id) in self.bot.db['members'].keys():
      await inter.response.send_message('Участника нет в датабазе. Как вы могли такое допустить?!',ephemeral=True)
    else:
      if amount == 0:
        await inter.response.send_message('Это так не работает./nВыберите сумму КРОМЕ НУЛЯ.',ephemeral=True)
      else:
        self.bot.db['members'][str(member.id)]['balance'] += amount
        await inter.response.send_message('Баланс изменён.',ephemeral=True)
        
  @commands.slash_command(
    name='balance_transfer',
    description='Перечисляет сухарики с вашего счёта на счёт участника',
    options=[
      disnake.Option('member', 'Участник, которому вы хотите перечислить сухарики', disnake.OptionType.user, True),
      disnake.Option('amount', 'Сколько перечислить', disnake.OptionType.integer, True, min_value=1)
    ])
  @commands.default_member_permissions(administrator=True)
  async def bal_trans(self, inter: disnake.AppCmdInter, member: disnake.User, amount: int):
    if member.bot:
      await inter.response.send_message('Это бот, а не участник. Пожалуйста, выберите кого-нибудь поодушевлённее.',ephemeral=True)
    elif not str(member.id) in self.bot.db['members'].keys():
      await inter.response.send_message('Участника нет в датабазе. Как вы могли такое допустить?!',ephemeral=True)
    elif member == inter.author:
      await inter.response.send_message('Деньги нельзя переводить самому себе. <:nikobruh:1013910937146773504>',ephemeral=True)
    elif self.bot.db['members'][str(inter.author.id)]['balance'] < amount:
      await inter.response.send_message('Недостаточно средств для перевода. \nНе хватило {0}<:kirieshka:1100873685201588285>'.format(amount-self.bot.db['members'][str(inter.author.id)]['balance']),ephemeral=True)
    else:
      self.bot.db['members'][str(inter.author.id)]['balance'] -= amount
      self.bot.db['members'][str(member.id)]['balance'] += amount
      await inter.response.send_message('Перевод совершён!\n`Ваш баланс:` {0} -> {1}<:kirieshka:1100873685201588285>\n`Баланс `{2}`:` {3} -> {4}<:kirieshka:1100873685201588285>'.format(self.bot.db['members'][str(inter.author.id)]['balance']+amount,self.bot.db['members'][str(inter.author.id)]['balance'],member.mention,self.bot.db['members'][str(member.id)]['balance']-amount,self.bot.db['members'][str(member.id)]['balance']),ephemeral=True)

  @commands.slash_command(
    name='give_bughunter',
    description='Выдаёт (или отнимает) ачивку "Дихлофос"',
    options=[
      disnake.Option('member', 'Участник, которому будет выдана ачивка', disnake.OptionType.user, True),
    ])
  @commands.default_member_permissions(administrator=True)
  @commands.is_owner()
  async def give_bughunter(self, inter: disnake.AppCmdInter, member: disnake.User):
    if member.bot:
      await inter.response.send_message('Это бот, а не участник. Пожалуйста, выберите кого-нибудь поодушевлённее.',ephemeral=True)
    elif not str(member.id) in self.bot.db['members'].keys():
      await inter.response.send_message('Участника нет в датабазе. Как вы могли такое допустить?!', ephemeral=True)
    else:
      if not self.bot.db['members'][str(member.id)]['achievements']['bugHunter']:
        self.bot.db['members'][str(member.id)]['achievements']['bugHunter'] = True
        await inter.response.send_message('Ачивка выдана. Хорошая работа.', ephemeral=True)
        embed = disnake.Embed(color=disnake.Color(0x474896))
        embed.description = 'Сообщить об ошибке внутри бота'
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/1017923933896441907/1102017693323902986/19_20220507223804.png')
        embed.set_author(name=f'{member.display_name} получил(а) достижение "Дихлофос"', icon_url=member.display_avatar)
        await inter.channel.send(embed=embed)
      else:
        self.bot.db['members'][str(member.id)]['achievements']['bugHunter'] = False
        await inter.response.send_message('Ачивка отнята.', ephemeral=True)

  @give_bughunter.error
  async def give_bughunter_error(self, inter: disnake.AppCmdInter, error: commands.CommandError):
    if isinstance(error, commands.NotOwner):
        await inter.response.send_message("Эта команда доступна только Чичерасту. <a:spongebruh:1068135572230639746>", ephemeral=True)

def setup(bot: commands.Bot):
  bot.add_cog(Admin(bot))