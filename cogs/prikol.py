import disnake
import asyncio
import random
from disnake.ext import commands
from typing import Optional

class Prikol(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot  

    def cog_load(self):
        print('Ког загружен: "{}"'.format(self.qualified_name))

    def cog_unload(self):
        print('Ког выгружен: "{}"'.format(self.qualified_name))

    @commands.slash_command(description='Дуэль с другим участником забавы ради :)')
    async def duel(self, inter: disnake.ApplicationCommandInteraction ):
        author = inter.author
        view = Confirm(author)
        await inter.response.send_message(f"`{inter.author}` готовится к игре в Револьветку... \nОсмелится ли кто-то принять вызов?", view=view)
        await view.wait()
        message = await inter.original_message()
        if view.value is None or view.value is False:
          await message.delete()
        else:
            view.clear_items()
            await message.edit(f"`{view.user}` согласился на игру с `{inter.author}`!", view=view)
            await asyncio.sleep(3)
            dealer = inter.author
            player = view.user
            health = random.randint(2,6)
            # health = 1
            dealer_health = health
            player_health = health
            round = 0
            barrel = []
            turn = random.choice([dealer,player])
            while dealer_health > 0 and player_health > 0:
                if barrel == []:
                    for x in range(0,random.randint(0,4)):
                        barrel.append(random.randint(0,1))
                    barrel.append(1)
                    barrel.append(0)
                    random.shuffle(barrel)
                    round += 1
                    await message.edit(f'{barrel.count(1)} патрон(а), {barrel.count(0)} пустой(-ых)')
                print(barrel)
                embed = disnake.Embed(color=disnake.Color(0x474896))
                embed.set_author(name=f'Револьветка - раунд {round}')
                print(f"{turn}'s turn!")
                embed.title = f'Ход `{turn}`!'
                embed.add_field(name=f'Заряды `{dealer}`:',value=('⚡' * dealer_health))
                embed.add_field(name=f'Заряды `{player}`:',value=('⚡' * player_health))
                view = Actions(turn,dealer,player)
                await message.edit(embed=embed,view=view)
                print('waiting for input...')
                await view.wait()
                view.clear_items()
                embed = None
                if view.value is None:
                    await message.edit(f'Техническое поражение - `{turn}` не среагировал в течении 3-х минут.\nПобеда присуждается `'+(str(dealer) if turn == player else str(player))+'`!',view=view,embed=embed)
                    break
                elif view.value is False:
                    if barrel[0] == 0:
                        await message.edit(f'{turn} выстрелил в себя... Повезло, это был пустой.',view=view)
                    elif barrel[0] == 1:
                        await message.edit(f'{turn} выстрелил в себя... Упс! Кажется у кого-то теперь дырка в голове.',view=view)
                        if turn == dealer:
                            dealer_health -= 1
                            turn = player
                        elif turn == player:
                            player_health -= 1
                            turn = dealer
                    barrel.pop(0)
                elif view.value is True:
                    if barrel[0] == 0:
                        await message.edit(f'{turn} выстрелил в оппонента... Это оказался пустой. Не повезло! (или повезло?)',view=view)
                        if turn == dealer:
                            turn = player
                        elif turn == player:
                            turn = dealer
                    elif barrel[0] == 1:
                        await message.edit(f'{turn} выстрелил в оппонента... Ух! Попал, да ещё как!',view=view)
                        if turn == dealer:
                            player_health -= 1
                            turn = player
                        elif turn == player:
                            dealer_health -= 1
                            turn = dealer
                    barrel.pop(0)
                await asyncio.sleep(3)
            view.clear_items()
            embed = None
            if dealer_health == 0:
                await message.edit(f'`{player}` обыграл `{dealer}` с {player_health} ХП в запасе! (Начальный лимит - {health})',view=view,embed=embed)
            elif player_health == 0:
                await message.edit(f'`{dealer}` обыграл `{player}` с {dealer_health} ХП в запасе! (Начальный лимит - {health})',view=view,embed=embed)

class Shoot(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=30.0)
        self.value: Optional[bool] = None

    @disnake.ui.button(label="В оппонента", style=disnake.ButtonStyle.blurple)
    async def shoot_op(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.value = True
        self.stop()
    
    @disnake.ui.button(label="В себя", style=disnake.ButtonStyle.gray)
    async def shoot_self(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.value = False
        self.stop()

class Actions(disnake.ui.View):
    def __init__(self,turn,dealer,player):
        self.turn = turn
        self.dealer = dealer
        self.player = player
        super().__init__(timeout=180.0)
        self.value: Optional[bool] = None
        self.user: Optional[int] = None

    @disnake.ui.button(label="Выстрелить!", style=disnake.ButtonStyle.red)
    async def shoot(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if inter.user == self.turn:
          view = Shoot()
          await inter.response.send_message('Куда стрелять будем?',view=view,ephemeral=True)
          await view.wait()
          if view.value is not None:
            if view.value == False: self.value = False
            if view.value == True: self.value = True
            message = await inter.original_message()
            await message.delete()
            self.stop()
        else:
            if inter.user == self.dealer or inter.user == self.player:
                await inter.response.send_message('Сейчас не ваш ход.', ephemeral=True)
            else:
                await inter.response.send_message('Вы не участвуете в игре.', ephemeral=True)
    
#    @disnake.ui.button(label="Использовать предмет", style=disnake.ButtonStyle.blurple)
#    async def inv_check(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
#       
#    @disnake.ui.button(label="Просмотреть инвентарь", style=disnake.ButtonStyle.gray)
#    async def inv_check(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
#      if inter.user.id == self.author.id:
#        self.value = False
#        self.stop()
#      else:
#        await inter.response.send_message('Отменить игру в силах лишь тот, кто предложил в неё сыграть.', ephemeral=True)

class Confirm(disnake.ui.View):
    def __init__(self, author):
        self.author = author
        super().__init__(timeout=60.0)
        self.value: Optional[bool] = None
        self.user: Optional[int] = None

    @disnake.ui.button(label="Присоединиться к игре", style=disnake.ButtonStyle.blurple)
    async def confirm(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if inter.user.id == self.author.id:
          await inter.response.send_message('Нельзя присоединиться к самому себе.', ephemeral=True)
        else:
          self.value = True
          self.user = inter.user
          self.stop()
        
    @disnake.ui.button(label="Отменить игру", style=disnake.ButtonStyle.red)
    async def cancel(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
      if inter.user.id == self.author.id:
        self.value = False
        self.stop()
      else:
        await inter.response.send_message('Отменить игру в силах лишь тот, кто предложил в неё сыграть.', ephemeral=True)

    @commands.slash_command(
    name='verification_create',
    description='Создаёт сообщение верификации')
    @commands.default_member_permissions(administrator=True)
    async def verif(self, ia: disnake.AppCmdInter):
        await ia.response.defer(ephemeral=True)
        await ia.channel.send('Спасибо, что дочитали до конца!\nТеперь пора получить роль Рандомовца, с которой вы получите все базовые права. \nНажмите на кнопку, и мы начнём процесс верификации. Не волнуйтесь, *больно не будет*.',
        components=[
        disnake.ui.Button(label='Верифицироваться', style=disnake.ButtonStyle.green, emoji='<:whothefu:1068100193192509450>', custom_id='verify')
        ]
        )
        await ia.edit_original_response('Сообщение отправлено.')
    
    @commands.Cog.listener('on_button_click')
    async def btn_listener(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == 'verify':
            if not inter.author.get_role(1014569986968268891):
              qs = QuestionSelect(question=1)
              view = disnake.ui.View(timeout=300.0)
              view.add_item(qs)
              await inter.response.send_message('Ну, посмотрим чему ты научился.\nЕсли вы не в курсе про разрешённость / запрещённость *определённого действия*, а в правилах про это не написано, что можно и нужно делать?',view=view,ephemeral=True)
              qs.message = await inter.original_response()
            else:
              await inter.response.send_message('Верификация уже пройдена. Нет нужды проходить её ещё раз. <:nikosmile:1161596483691360276> ', ephemeral=True)

class QuestionSelect(disnake.ui.StringSelect):
    message: disnake.Message = None
    score: int = 0

    def __init__(self, question: int = 1):
        self.question = question
        options = []

        if question == 1:
            options = [
                disnake.SelectOption(label='Если не написано, значит можно', value='q1_a1'),
                disnake.SelectOption(label='Сделаю один раз', description='если не наказали - значит можно', value='q1_a2'),
                disnake.SelectOption(label='Спрошу у админа', description='он лучше знает', value='q1_a3'),
                disnake.SelectOption(label='Я сам себе админ', description='чё хочу, то и творю', value='q1_a4'),
            ]
        elif question == 2:
            options = [
                disnake.SelectOption(label='Сообщить админам', description='через тикет или пинг роли', value='q2_a1'),
                disnake.SelectOption(label='Наблюдать', description='само успокоится', value='q2_a2'),
                disnake.SelectOption(label='Вступить в конфликт', description='чтобы было веселее', value='q2_a3'),
                disnake.SelectOption(label='Решить всё самому', description='да кому нужны эти админы?', value='q2_a4'),
            ]
        elif question == 3:
            options = [
                disnake.SelectOption(label='чё?', value='q3_a1'),
                disnake.SelectOption(label='цифра 6, весьма полезное', value='q3_a2'),
                disnake.SelectOption(label='цифра 9, очень крутая', value='q3_a3'),
                disnake.SelectOption(label='та что про доброту :)', value='q3_a4'),
            ]

        super().__init__(
            placeholder='[Выберите ответ:]',
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, ia: disnake.MessageInteraction):
        if self.question == 1:
            if ia.values[0] == 'q1_a3':
                self.score += 1

            qs = QuestionSelect(question=2)
            qs.score = self.score
            qs.message = self.message
            view = disnake.ui.View()
            view.add_item(qs)
            try:
                await ia.send()
            except Exception:
                pass
            await self.message.edit('Вы видите, что в чате начался сущий кошмар: участники оскорбляют друг друга, матерятся, да и вообще не соблюдают интернет-манеры! \nЧто нужно сделать **в первую очередь**?', view=view)
        elif self.question == 2:
            if ia.values[0] == 'q2_a1':
                self.score += 1

            qs = QuestionSelect(question=3)
            qs.score = self.score
            qs.message = self.message
            view = disnake.ui.View()
            view.add_item(qs)
            try:
                await ia.send()
            except Exception:
                pass
            await self.message.edit('Самое полезное и лучшее правило (по вашему скромному мнению)?', view=view)
        elif self.question == 3:
            if ia.values[0] != 'q3_a1':
                self.score += 1

            try:
                await ia.send()
            except Exception:
                pass

            if self.score >= 2:
                role = ia.guild.get_role(1014569986968268891)
                await ia.author.add_roles(role)
                await self.message.edit(':ballot_box_with_check: Поздравляю с прохождением верификации! Теперь ты полноценный член нашего рандомного общества. Приятного общения!', view=None)
            else:
                await self.message.edit(':x: Где-то вы ошиблись. Попробуйте ещё раз. <:nikoeepy:1181309167152136264>', view=None)

def setup(bot: commands.Bot):
    bot.add_cog(Prikol(bot))