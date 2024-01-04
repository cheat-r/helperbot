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
        await inter.response.send_message(f"`{inter.author}` готовится к дуэли... \nОсмелится ли кто-то принять вызов?", view=view)
        await view.wait()
        message = await inter.original_message()
        if view.value is None or view.value is False:
          await message.delete()
        else:
            view.clear_items()
            await message.edit(f"`{view.user}` принял дуэль!", view=view)
            await asyncio.sleep(3)
            if random.randrange(1,3) == 1:
              attack = inter.author
              defence = view.user
            else:
                attack = view.user
                defence = inter.author
            await message.edit(f"Жребий брошен! Первым стреляет `{attack}`.")
            await asyncio.sleep(3)
            fight = True
            while fight == True:
              x=0
              if random.randrange(1,6) == 5:
                await message.edit(f"`{defence}` начинает уворачиваться! Шанс попадания снижен до 25%.")
                x=2
              else:
                 await message.edit(f"`{defence}` предпочёл постоять. Шанс попадания - 50%")
              await asyncio.sleep(3)
              if random.randrange(1,3+x) == 1:
                  await message.edit(f"БАХ! `{attack}` попал прямо в голову...")
                  await asyncio.sleep(3)
                  await message.edit(f"Победа присуждается `{attack}`! \nПроигравший - `{defence}`.")
                  fight = False
                  break
              else:
                  await message.edit(f"БАХ! Кажется, не попал... Ход переходит `{defence}`.")
              x=0
              await asyncio.sleep(3)
              if random.randrange(1,6) == 5:
                await message.edit(f"`{attack}` начинает уворачиваться! Шанс попадания снижен до 25%.")
                x=2
              else:
                 await message.edit(f"`{attack}` предпочёл постоять. Шанс попадания - 50%")
              await asyncio.sleep(3)
              if random.randrange(1,3+x) == 1:
                  await message.edit(f"БАХ! `{defence}` попал прямо в голову...")
                  await asyncio.sleep(3)
                  await message.edit(f"Победа присуждается `{defence}`! \nПроигравший - `{attack}`.")
                  fight = False
                  break
              else:
                  await message.edit(f"БАХ! Кажется, не попал... Ход переходит `{attack}`.")
                  await asyncio.sleep(3)
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
            # Вопрос 1
            options = [
                disnake.SelectOption(label='Если не написано, значит можно', value='q1_a1'),
                disnake.SelectOption(label='Сделаю один раз', description='если не наказали - значит можно', value='q1_a2'),
                disnake.SelectOption(label='Спрошу у админа', description='он лучше знает', value='q1_a3'),
                disnake.SelectOption(label='Я сам себе админ', description='чё хочу, то и творю', value='q1_a4'),
            ]
        elif question == 2:
            # Вопрос 2
            options = [
                disnake.SelectOption(label='Сообщить админам', description='через тикет или пинг роли', value='q2_a1'),
                disnake.SelectOption(label='Наблюдать', description='само успокоится', value='q2_a2'),
                disnake.SelectOption(label='Вступить в конфликт', description='чтобы было веселее', value='q2_a3'),
                disnake.SelectOption(label='Решить всё самому', description='да кому нужны эти админы?', value='q2_a4'),
            ]
        elif question == 3:
            # Вопрос 3
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

class Confirm(disnake.ui.View):
    def __init__(self, author):
        self.author = author
        super().__init__(timeout=60.0)
        self.value: Optional[bool] = None
        self.user: Optional[int] = None

    @disnake.ui.button(label="Принять вызов!", style=disnake.ButtonStyle.blurple)
    async def confirm(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if inter.user.id == self.author.id:
          await inter.response.send_message('Нельзя принять вызов у самого себя.', ephemeral=True)
        else:
          self.value = True
          self.user = inter.user
          self.stop()
        
    @disnake.ui.button(label="Отменить дуэль", style=disnake.ButtonStyle.red)
    async def cancel(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
      if inter.user.id == self.author.id:
        self.value = False
        self.stop()
      else:
        await inter.response.send_message('Отменить дуэль в силах лишь её зачинщик.', ephemeral=True)

def setup(bot: commands.Bot):
    bot.add_cog(Prikol(bot))