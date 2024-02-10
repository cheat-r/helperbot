import disnake
import random
from disnake.ext import commands
from typing import Optional

class Inventory(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  def cog_load(self):
    print('Ког загружен: "{}"'.format(self.qualified_name))

  def cog_unload(self):
    print('Ког выгружен: "{}"'.format(self.qualified_name))

  @commands.slash_command(
    name='inventory',
    description='Показывает карманы с предметами (ваши или чужие)',
    options=[
      disnake.Option('member', 'Участник, в чьи карманы необходимо залезть', disnake.OptionType.user, False),
    ])
  async def inventory(self, inter: disnake.AppCmdInter, member: disnake.User = None):
    if member == None or member == inter.author:
      self.bot.add_user_to_db(inter.author.id)
      items=self.bot.db
      user=str(inter.author.id)
      dropdown = InvDropdown(items, user)
      view = disnake.ui.View(timeout=None)
      view.add_item(dropdown)
      embed = disnake.Embed(color=disnake.Color(0x474896))
      embed.set_author(name=f'Инвентарь {inter.author.display_name}', icon_url=inter.author.display_avatar)  
      for i in self.bot.db['members'][str(inter.author.id)]['inventory']:
        embed.add_field(name=str(self.bot.db['items'][str(i)]['name'])+' ('+str(self.bot.db['members'][str(inter.author.id)]['inventory'][str(i)])+' шт.)', value=str(self.bot.db['items'][str(i)]['description']), inline=False)
      if not self.bot.db['members'][str(inter.author.id)]['inventory']:
        embed.add_field(name='...мда, пустовато.', value='Хотя это поправимо. Советую закупиться в магазине.', inline=False)
        await inter.response.send_message(embed=embed, ephemeral=True)
      else:
        await inter.response.send_message(embed=embed, view=view, ephemeral=True)
    else:
      if member.bot:
        await inter.response.send_message('Это бот, а не участник. Пожалуйста, выберите кого-нибудь поодушевлённее.',ephemeral=True)
      elif not str(member.id) in self.bot.db['members'].keys():
        await inter.response.send_message('Участника нет в датабазе. Как вы могли такое допустить?!',ephemeral=True)
      else:
        items=self.bot.db
        user=str(member.id)
        embed = disnake.Embed(color=disnake.Color(0x474896))
        embed.set_author(name=f'Инвентарь {member.display_name}', icon_url=member.display_avatar)  
        for i in self.bot.db['members'][str(member.id)]['inventory']:
          embed.add_field(name=str(self.bot.db['items'][str(i)]['name'])+' ('+str(self.bot.db['members'][str(member.id)]['inventory'][str(i)])+' шт.)', value=str(self.bot.db['items'][str(i)]['description']), inline=False)
        if not self.bot.db['members'][str(member.id)]['inventory']:
          embed.add_field(name='...мда, пустовато.', value='Даже посмотреть не на что.', inline=False)
        await inter.response.send_message(embed=embed, ephemeral=True)
  @commands.user_command(name="Глянуть инвентарь")
  async def ctx_inventory(self, inter: disnake.AppCmdInter, member: disnake.User):
    if member == inter.author:
      self.bot.add_user_to_db(inter.author.id)
      items=self.bot.db
      user=str(inter.author.id)
      dropdown = InvDropdown(items, user)
      view = disnake.ui.View(timeout=None)
      view.add_item(dropdown)
      embed = disnake.Embed(color=disnake.Color(0x474896))
      embed.set_author(name=f'Инвентарь {inter.author.display_name}', icon_url=inter.author.display_avatar)  
      for i in self.bot.db['members'][str(inter.author.id)]['inventory']:
        embed.add_field(name=str(self.bot.db['items'][str(i)]['name'])+' ('+str(self.bot.db['members'][str(inter.author.id)]['inventory'][str(i)])+' шт.)', value=str(self.bot.db['items'][str(i)]['description']), inline=False)
      if not self.bot.db['members'][str(inter.author.id)]['inventory']:
        embed.add_field(name='...мда, пустовато.', value='Хотя это поправимо. Советую закупиться в магазине.', inline=False)
        await inter.response.send_message(embed=embed, ephemeral=True)
      else:
        await inter.response.send_message(embed=embed, view=view, ephemeral=True)
    else:
      if member.bot:
        await inter.response.send_message('Это бот, а не участник. Пожалуйста, выберите кого-нибудь поодушевлённее.',ephemeral=True)
      elif not str(member.id) in self.bot.db['members'].keys():
        await inter.response.send_message('Участника нет в датабазе. Как вы могли такое допустить?!',ephemeral=True)
      else:
        items=self.bot.db
        user=str(member.id)
        embed = disnake.Embed(color=disnake.Color(0x474896))
        embed.set_author(name=f'Инвентарь {member.display_name}', icon_url=member.display_avatar)  
        for i in self.bot.db['members'][str(member.id)]['inventory']:
          embed.add_field(name=str(self.bot.db['items'][str(i)]['name'])+' ('+str(self.bot.db['members'][str(member.id)]['inventory'][str(i)])+' шт.)', value=str(self.bot.db['items'][str(i)]['description']), inline=False)
        if not self.bot.db['members'][str(member.id)]['inventory']:
          embed.add_field(name='...мда, пустовато.', value='Даже посмотреть не на что.', inline=False)
        await inter.response.send_message(embed=embed, ephemeral=True)

  @commands.slash_command(name='shop', description='Каталог товаров, доступных к приобретению')
  async def shop(self, inter: disnake.AppCmdInter):
    self.bot.add_user_to_db(inter.author.id)
    items=self.bot.db
    dropdown = ShopDropdown(items)
    view = disnake.ui.View(timeout=None)
    view.add_item(dropdown)
    embed = disnake.Embed(color=disnake.Color(0x474896))
    embed.set_author(name='Магазин')
    for i in self.bot.db['items']:
      embed.add_field(name=str(self.bot.db['items'][str(i)]['name'])+': '+str(self.bot.db['items'][str(i)]['price'])+'<:kirieshka:1100873685201588285>', value=str(self.bot.db['items'][str(i)]['description']), inline=False)
    await inter.response.send_message(embed=embed, view=view, ephemeral=True)

class CustomRoleModal(disnake.ui.Modal):
    def __init__(self, bot) -> None:
        self.bot = bot
        components = [
            disnake.ui.TextInput(
                label="Имя",
                placeholder="Название вашей роли",
                custom_id="name",
                style=disnake.TextInputStyle.short,
                min_length=1,
                max_length=30,
                required=True,
            ),
            disnake.ui.TextInput(
                label="Цвет (Hex-код без #)",
                placeholder="Оставьте пустым для цвета по умолчанию",
                custom_id="color",
                style=disnake.TextInputStyle.short,
                min_length=6,
                max_length=6,
                required=False,
            ),
        ]
        super().__init__(title="Создание роли", custom_id="customrole", components=components, timeout=3600)
    async def callback(self, inter: disnake.ModalInteraction) -> None:
      role_name = '[custom] '+str(inter.text_values["name"])
      role_color = inter.text_values["color"]
      if role_color:
        role_color = disnake.Color(int(role_color, 16))
        role = await inter.guild.create_role(name=role_name,color=role_color)
      else:
        role = await inter.guild.create_role(name=role_name)
      await inter.author.add_roles(role)
      await inter.response.send_message('Роль создана!', ephemeral=True)

    async def on_error(self, error: Exception, inter: disnake.ModalInteraction) -> None:
        if not 'customRole' in self.bot.db['members'][str(inter.user.id)]['inventory']:
          self.bot.db['members'][str(inter.user.id)]['inventory']['customRole'] = 1
        else:
          self.bot.db['members'][str(inter.user.id)]['inventory']['customRole'] += 1
        await inter.response.send_message("Ты указал неправильный Hex-код. Талон был возвращён.", ephemeral=True)

class ShopConfirm(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=10.0)
        self.value: Optional[bool] = None

    @disnake.ui.button(label="Да, купить", style=disnake.ButtonStyle.green)
    async def confirm(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.value = True
        self.stop()

    @disnake.ui.button(label="Нет, я передумал", style=disnake.ButtonStyle.red)
    async def cancel(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.value = False
        self.stop()

class InvConfirm(disnake.ui.View):
    def __init__(self, item, bot):
        self.item = item
        self.bot = bot
        super().__init__(timeout=10.0)
        self.value: Optional[bool] = None

    @disnake.ui.button(label="Да, использовать", style=disnake.ButtonStyle.green)
    async def confirm(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
      self.value = True
      if not str(self.item) in self.bot['members'][str(inter.user.id)]['inventory']:
        self.stop()
      else:
        if self.item == 'customRole':
          await inter.response.send_modal(modal=CustomRoleModal(self.bot))
        elif self.item == 'breadPack':
          win = random.randint(250,750)
          self.bot['members'][str(inter.author.id)]['balance'] += win
          await inter.response.send_message('В пачке вам попалось {}<:kirieshka:1100873685201588285>'.format(win), ephemeral=True)
        elif self.item == 'lotteryRole':
          if random.randint(1,4) == 4:
            if not 'customRole' in self.bot['members'][str(inter.user.id)]['inventory']:
              self.bot['members'][str(inter.user.id)]['inventory']['customRole'] = 1
            else:
              self.bot['members'][str(inter.user.id)]['inventory']['customRole'] += 1
            await inter.response.send_message('Вам крайне повезло, вы выиграли `Талон на кастомную роль`!', ephemeral=True)
          else:
            await inter.response.send_message('Увы, билет оказался проигрышным. Вам не повезло.', ephemeral=True)
        elif self.item == 'beer':
          options = ['Уж очень оно вкусное...',
          'Не волнуйтесь, оно безалкогольное.',
          '...Или это всё же квас?',
          'А дальше я не придумал.',
          '<:omor:1112465534504665099>',
          'Надо будет ещё бутылку купить.',
          "so, you lot gonna scroll by without sayin' \nvvyeerraarrsesssarsdaandimthgrasssmannpunkyeeeyahhavint",
          'В приступе кайфа слышится тихий, но явный звук: \n**ж.** \nЧто (или кто) это было - не знает даже источник звука.']
          embed = disnake.Embed(color=disnake.Color(0x474896))
          embed.description = options[random.randint(0, len(options)-1)]
          embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/1017923933896441907/1112829028555034684/beer.gif')
          embed.set_author(name=f'{inter.author.display_name} выпил(а) бутылку пива', icon_url=inter.author.display_avatar)
          await inter.channel.send(embed=embed)
        self.stop()

    @disnake.ui.button(label="Нет, я передумал", style=disnake.ButtonStyle.red)
    async def cancel(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.value = False
        self.stop()

class InvDropdown(disnake.ui.StringSelect):
    def __init__(self, items, user):
      self.user = user
      self.items = items
      options = []
      for i in items['members'][user]['inventory']:
        options.append(
          disnake.SelectOption(
            label=items['items'][str(i)]['name'],
            description='Кол-во: '+str(items['members'][user]['inventory'][str(i)])+' шт.',
            value=str(i)
          )
        )
      super().__init__(
        placeholder="[Использовать предмет:]",
        min_values=1,
        max_values=1,
        options=options,
      )
    async def callback(self, inter: disnake.MessageInteraction):
      view = InvConfirm(item=self.values[0],bot=self.items)
      message = await inter.response.send_message('Вы уверены что хотите израсходовать предмет "{}"?'.format(self.items['items'][self.values[0]]['name']), view=view, ephemeral=True)
      await view.wait()
      message = await inter.original_message()
      if view.value is None:
        await message.delete()
      elif view.value:
        if not str(self.values[0]) in self.items['members'][str(inter.user.id)]['inventory']:
          await message.edit('Удивительно, но у вас кончились запасы этого предмета, поэтому расходовать оказалось нечего.', view=None)
          return
        elif self.items['members'][str(inter.user.id)]['inventory'][self.values[0]] == 1:
          del self.items['members'][str(inter.user.id)]['inventory'][self.values[0]]
        else:
          self.items['members'][str(inter.user.id)]['inventory'][self.values[0]] -= 1
        await message.edit('Вы израсходовали этот предмет.', view=None)
      else:
        await message.delete()

class ShopDropdown(disnake.ui.StringSelect):
    def __init__(self, items):
      self.items = items
      options = []
      for i in items['items']:
        options.append(
          disnake.SelectOption(
            label=items['items'][str(i)]['name'],
            description='Стоимость: '+str(items['items'][str(i)]['price'])+' сухариков',
            value=str(i)  
          )
        )
      super().__init__(
        placeholder="Хотите что-нибудь купить?",
        min_values=1,
        max_values=1,
        options=options,
      )
    async def callback(self, inter: disnake.MessageInteraction):
      view = ShopConfirm()
      if self.values[0] == 'misterio':
        if inter.author.get_role(1114655677143601245):
          await inter.response.send_message('Вы уже являетесь членом ночного уголка. Вам незачем покупать пропуск ещё раз.', ephemeral=True)
          return
      if self.items['members'][str(inter.user.id)]['balance'] < self.items['items'][self.values[0]]['price']:
        await inter.response.send_message('У тебя недостаточно сухариков... Иди подзаработай их в чате. Как раз актив нам поднимешь.', ephemeral=True)
      else:
        message = await inter.response.send_message('Вы уверены что хотите купить предмет "{}"?'.format(self.items['items'][self.values[0]]['name']), view=view, ephemeral=True)
        await view.wait()
        message = await inter.original_message()
        if view.value is None:
          await message.delete()
        elif view.value:
          if self.items['members'][str(inter.user.id)]['balance'] < self.items['items'][self.values[0]]['price']:
            await message.edit('У тебя недостаточно сухариков... Либо ты попытался обмануть систему, либо не заметил как успел всё потратить.', view=None)
            return
          self.items['members'][str(inter.user.id)]['balance'] -= self.items['items'][self.values[0]]['price']
          if self.values[0] == 'misterio':
            await inter.author.add_roles(inter.guild.get_role(1114655677143601245), reason='стал участником клуба мистерио')
            await message.edit('Поздравляем с приобретением! Теперь вы участник ночного уголка. Был выдан доступ к <#1114655915069685892>.\n(заранее прочитайте закреплённое сообщение, чтобы ознакомиться с правилами клуба)', view=None)
            return
          if not self.values[0] in self.items['members'][str(inter.user.id)]['inventory']:
            self.items['members'][str(inter.user.id)]['inventory'][self.values[0]] = 1
          else:
            self.items['members'][str(inter.user.id)]['inventory'][self.values[0]] += 1
          await message.edit('Поздравляем с приобретением!', view=None)
        else:
          await message.delete()

def setup(bot: commands.Bot):
  bot.add_cog(Inventory(bot))