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

    @commands.slash_command(
    name='verification_create',
    description='Создаёт сообщение верификации')
    @commands.default_member_permissions(administrator=True)
    async def verif(self, inter: disnake.AppCmdInter):
        await inter.response.defer(ephemeral=True)
        await inter.channel.send('Спасибо, что дочитали до конца!\nТеперь пора получить роль Рандомовца, с которой вы получите все базовые права. \nНажмите на кнопку, и мы начнём процесс верификации. Не волнуйтесь, *больно не будет*.',
        components=[
        disnake.ui.Button(label='Верифицироваться', style=disnake.ButtonStyle.green, emoji='<:whothefu:1068100193192509450>', custom_id='verify')
        ]
        )
        await inter.edit_original_response('Сообщение отправлено.')
    
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

    @commands.slash_command(description='Игра в Револьветку с другим участником. Перенос Buckshot Roulette прямо к вам в чат!', options=[
        disnake.Option('duel_member', 'Бросить вызов определённому участнику! Оставьте пустым, чтобы любой участник мог принять вызов', disnake.OptionType.user),
        disnake.Option('starting_hp', 'Начальное кол-во зарядов (рандомизировано если не уточнено)', disnake.OptionType.integer, min_value=2, max_value=6),
        disnake.Option('items_per_round', 'Кол-во предметов за раунд (0 отключает предметы, оставьте пустым для рандомизации)', disnake.OptionType.integer, min_value=0, max_value=4),
        disnake.Option('bullets_per_round', 'Кол-во патрон в обойме за раунд, оставьте пустым для рандомизации', disnake.OptionType.integer, min_value=2, max_value=8)
    ])
    async def duel(self, inter: disnake.ApplicationCommandInteraction, duel_member: disnake.User = None, starting_hp: int = None, items_per_round: int = None, bullets_per_round: int = None):
        if duel_member:
            if duel_member == inter.author:
                await inter.response.send_message('Чё, самый умный нашёлся? Нельзя бросить вызов самому себе.',ephemeral=True)
            elif duel_member.bot:
                await inter.response.send_message('К сожалению (или к счастью), с ботами нельзя дуэлиться. Пожалуйста, выберите живого участника.',ephemeral=True)
        author = inter.author
        comview = Confirm(author,duel_member)
        embed = disnake.Embed(color=disnake.Color(0x474896))
        embed.set_author(name='Кастомные правила')
        if starting_hp:
            embed.add_field(name='Начальное кол-во зарядов:',value=str(starting_hp))
        if items_per_round != None:
            embed.add_field(name='Кол-во предметов за раунд:',value='[Предметы отключены]' if items_per_round == 0 else str(items_per_round))
        if bullets_per_round:
            embed.add_field(name='Кол-во патронов за раунд:',value=str(bullets_per_round))
        if not starting_hp and items_per_round is None and not bullets_per_round:
            embed.add_field(name='Ванильная игра!',value='Хост не установил кастомных правил, всё будет рандомизировано как при бесконечном режиме.')
        await inter.response.send_message((f'{inter.author} бросил вызов {duel_member}!\nОсмелится ли он принять вызов?' if duel_member else f"`{inter.author}` готовится к дуэли...\nОсмелится ли кто-то принять вызов?"), view=comview, embed=embed)
        await comview.wait()
        message = await inter.original_message()
        if comview.value is None or comview.value is False:
          await message.delete()
        else:
            comview.clear_items()
            await message.edit(f"`{comview.user}` согласился на игру с `{inter.author}`!", view=comview)
            await asyncio.sleep(3)
            dealer = inter.author
            player = comview.user
            if starting_hp: health = starting_hp
            else: health = random.randint(2,6)
            dealer_health = health
            player_health = health
            handcuffed = 0
            doubled = 0
            dealer_inv = {
                "glass": 0, # отображает кол-во патрон в барабане и текущий патрон
                "beer": 0, # сбрасывает текущий патрон, завершает раунд если барабан пустой
                "doubler": 0, # удваивает урон на один заряженный выстрел или до конца хода
                "shield": 0, # принимает на себя одну единицу урона от выстрела (удвоенный патрон нанесёт 1 урон), сбрасывается в начале следующего хода
                "handcuffs": 0, # пропускает ход оппонента (доп выстрел)
                "shielded": 0,
                "total": 0 # лимит предметов, больше 8 штук будет скидываться в мою личную яму >:D
            }
            player_inv = {
                "glass": 0,
                "beer": 0,
                "doubler": 0,
                "shield": 0,
                "handcuffs": 0,
                "shielded": 0,
                "total": 0
            }
            round = 0
            barrel = []
            turn = random.choice([dealer,player])
            while dealer_health > 0 and player_health > 0:
                if barrel == []:
                    if bullets_per_round:
                        reload = bullets_per_round - 2
                    else:
                        reload = random.randint(0,4)
                    if items_per_round != None:
                        items = items_per_round
                    else:
                        items = random.randint(1,4)
                    for x in range(items): # выдача предметов
                        if dealer_inv['total'] < 8:
                            dealer_inv[random.choice(['glass','beer','doubler','shield','handcuffs'])] += 1
                            dealer_inv['total'] += 1
                        if player_inv['total'] < 8:
                            player_inv[random.choice(['glass','beer','doubler','shield','handcuffs'])] += 1
                            player_inv['total'] += 1
                    for x in range(reload): # зарядка барабана
                        if barrel.count(1) > barrel.count(0):
                            barrel.append(0)
                        elif barrel.count(0) - barrel.count(1) == 2:
                            barrel.append(1)
                        else:
                            barrel.append(random.randint(0,1))
                    barrel.append(1)
                    barrel.append(0)
                    random.shuffle(barrel)
                    round += 1
                    if doubled:
                        doubled = 0
                    if handcuffed:
                        handcuffed = 0
                        if turn == player: turn = dealer
                        else: turn = player
                    await message.edit(f'{barrel.count(1)} патрон(а), {barrel.count(0)} пустой(-ых)')
                embed = disnake.Embed(color=disnake.Color(0x474896))
                embed.set_author(name=f'Револьветка - раунд {round}')
                embed.title = f'Ход `{turn}`!'+(' (Выстрел усилен)' if doubled else '')+(' (Оппонент в наручниках)' if handcuffed==2 else '\n(Оппонент в наручниках, но скоро выберется)' if handcuffed==1 else '')
                embed.add_field(name=f'Заряды `{dealer}`:',value=('⚡' * dealer_health)+('🛡️' if dealer_inv['shielded'] else ''))
                embed.add_field(name=f'Заряды `{player}`:',value=('⚡' * player_health)+('🛡️' if player_inv['shielded'] else ''))
                view = Actions(turn,dealer,player,dealer_inv,player_inv,barrel,doubled,handcuffed)
                await message.edit(embed=embed,view=view)
                await view.wait()
                view.clear_items()
                embed = None
                if view.value == 'Timeout':
                    embed = disnake.Embed(color=disnake.Color(0x474896))
                    embed.set_author(name='Циферки ради интереса...')
                    embed.add_field(name=f'Статистика `{dealer}`:',value=f'Зярядов: {dealer_health}\nПредметов: {dealer_inv["total"]}')
                    embed.add_field(name=f'Статистика `{player}`:',value=f'Зярядов: {player_health}\nПредметов: {player_inv["total"]}')
                    embed.add_field(name='Начальное кол-во зарядов:',value=str(health),inline=False)
                    if items_per_round != None:
                        embed.add_field(name='Кол-во предметов за раунд:',value='[Предметы отключены]' if items_per_round == 0 else str(items_per_round))
                    if bullets_per_round:
                        embed.add_field(name='Кол-во патронов за раунд:',value=str(bullets_per_round))
                    await message.edit(f'Техническое поражение - `{turn}` не среагировал в течении 3-х минут.\nПобеда присуждается `'+(str(dealer) if turn == player else str(player))+'`!',view=view,embed=embed)
                    break
                elif view.value == 'Self':
                    if barrel[0] == 0:
                        await message.edit(f'{turn} выстрелил в себя...\nЭто был пустой, идём дальше.',view=view)
                    elif barrel[0] == 1:
                        await message.edit(f'{turn} выстрелил в себя...\n💀 <- молодец, дебил, попал!',view=view)
                        if turn == dealer:
                            dealer_health -= (1 + doubled - dealer_inv['shielded'])
                            dealer_inv['shielded'] = 0
                            player_inv['shielded'] = 0
                            if handcuffed:
                                handcuffed -= 1
                                if not handcuffed: turn = player
                            else: turn = player
                        elif turn == player:
                            player_health -= (1 + doubled - player_inv['shielded'])
                            dealer_inv['shielded'] = 0
                            player_inv['shielded'] = 0
                            if handcuffed:
                                handcuffed -= 1
                                if not handcuffed: turn = dealer
                            else: turn = dealer
                        doubled = 0
                    barrel.pop(0)
                elif view.value == 'Opposite':
                    if barrel[0] == 0:
                        await message.edit(f'{turn} выстрелил в оппонента..?\nХотя нет, не выстрелил. Это был пустой.',view=view)
                        if turn == dealer:
                            player_inv['shielded'] = 0
                            if handcuffed:
                                handcuffed -= 1
                                if not handcuffed: turn = player
                            else: turn = player
                        elif turn == player:
                            dealer_inv['shielded'] = 0
                            if handcuffed:
                                handcuffed -= 1
                                if not handcuffed: turn = dealer
                            else: turn = dealer
                        doubled = 0
                    elif barrel[0] == 1:
                        await message.edit(f'{turn} выстрелил в оппонента... 💥\nУпс. Оно само, честно.',view=view)
                        if turn == dealer:
                            player_health -= (1 + doubled - player_inv['shielded'])
                            player_inv['shielded'] = 0
                            if handcuffed:
                                handcuffed -= 1
                                if not handcuffed: turn = player
                            else: turn = player
                        elif turn == player:
                            dealer_health -= (1 + doubled - dealer_inv['shielded'])
                            dealer_inv['shielded'] = 0
                            if handcuffed:
                                handcuffed -= 1
                                if not handcuffed: turn = dealer
                            else: turn = dealer
                        doubled = 0
                    barrel.pop(0)
                elif view.value == 'Beer':
                    await message.edit(f'{turn} сделал "контрольный" выстрел.\n\n'+('Пуля полетела прямо в стену. Страшно.' if barrel[0]==1 else 'Выстрел не произошёл. Всё ещё страшно.'),view=view)
                    barrel.pop(0)
                elif view.value == 'Doubler':
                    doubled = 1
                    await message.edit(f'{turn} удвоил урон следующего выстрела!',view=view)
                elif view.value == 'Shield':
                    if turn == dealer:
                        dealer_inv['shielded'] = 1
                    elif turn == player:
                        player_inv['shielded'] = 1
                    await message.edit(f'{turn} перестраховался щитом!',view=view)
                elif view.value == 'Handcuffs':
                    handcuffed = 2
                    await message.edit(f'{turn} нацепил наручники на своего оппонента!',view=view)
                await asyncio.sleep(3)
            view.clear_items()
            embed = disnake.Embed(color=disnake.Color(0x474896))
            embed.set_author(name='Кастомные правила игры')
            if starting_hp:
                embed.add_field(name='Начальное кол-во зарядов:',value=str(starting_hp))
            if items_per_round != None:
                embed.add_field(name='Кол-во предметов за раунд:',value='[Предметы отключены]' if items_per_round == 0 else str(items_per_round))
            if bullets_per_round:
                embed.add_field(name='Кол-во патронов за раунд:',value=str(bullets_per_round))
            if not starting_hp and items_per_round is None and not bullets_per_round:
                embed = None
            if round == 3:
                round = str(round) + '-ем'
            else: round = str(round) + '-ом'
            if dealer_health == 0:
                await message.edit(f'`{player}` обыграл `{dealer}` на {round} раунде с {player_health} HP в запасе!',view=view,embed=embed)
            elif player_health == 0:
                await message.edit(f'`{dealer}` обыграл `{player}` на {round} раунде с {dealer_health} HP в запасе!',view=view,embed=embed)

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

class Use(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=60.0)
        self.value: Optional[str] = None

    @disnake.ui.button(label="Стекло", style=disnake.ButtonStyle.gray)
    async def glass(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.value = 'glass'
        self.stop()
    
    @disnake.ui.button(label="Пиво", style=disnake.ButtonStyle.gray)
    async def beer(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.value = 'beer'
        self.stop()
    
    @disnake.ui.button(label="Удвоитель", style=disnake.ButtonStyle.gray)
    async def doubler(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.value = 'doubler'
        self.stop()
    
    @disnake.ui.button(label="Щит", style=disnake.ButtonStyle.gray)
    async def shield(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.value = 'shield'
        self.stop()
    
    @disnake.ui.button(label="Наручники", style=disnake.ButtonStyle.gray)
    async def handcuffs(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.value = 'handcuffs'
        self.stop()

class Actions(disnake.ui.View):
    def __init__(self,turn,dealer,player,dealer_inv,player_inv,barrel,doubled,handcuffed):
        self.turn = turn
        self.dealer = dealer
        self.player = player
        self.dealer_inv = dealer_inv
        self.player_inv = player_inv
        self.barrel = barrel
        self.doubled = doubled
        self.handcuffed = handcuffed
        super().__init__(timeout=180.0)
        self.value: Optional[str] = 'Timeout'

    @disnake.ui.button(label="Выстрелить!", style=disnake.ButtonStyle.red)
    async def shoot(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if inter.user == self.turn:
          view = Shoot()
          await inter.response.send_message('Куда стрелять будем?',view=view,ephemeral=True)
          await view.wait()
          if view.value is not None:
            if view.value == False: self.value = 'Self'
            if view.value == True: self.value = 'Opposite'
            message = await inter.original_message()
            await message.delete()
            self.stop()
        else:
            if inter.user == self.dealer or inter.user == self.player:
                await inter.response.send_message('Сейчас не ваш ход.', ephemeral=True)
            else:
                await inter.response.send_message('Вы не участвуете в игре.', ephemeral=True)
    
    @disnake.ui.button(label="Использовать предмет", style=disnake.ButtonStyle.gray)
    async def inv_use(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if inter.user == self.turn:
          if inter.user == self.dealer:
                if self.dealer_inv['total'] == 0:
                    await inter.response.send_message('Инвентарь пуст, использовать нечего. <:HUH:1187112357541974077>',ephemeral=True)
                else:
                    inv = self.dealer_inv
                    view = Use()
                    embed = disnake.Embed(color=disnake.Color(0x474896))
                    embed.add_field(name=f'Стекло ({self.dealer_inv["glass"]} шт.)',value='Отображает кол-во патрон в барабане и **текущий патрон**',inline=False)
                    embed.add_field(name=f'Пиво ({self.dealer_inv["beer"]} шт.)',value='Сбрасывает текущий патрон, завершает раунд если барабан пустой',inline=False)
                    embed.add_field(name=f'Удвоитель ({self.dealer_inv["doubler"]} шт.)',value='Удваивает урон на один заряженный выстрел или до конца хода'+(' [Применён]' if self.doubled else ''),inline=False)
                    embed.add_field(name=f'Щит ({self.dealer_inv["shield"]} шт.)',value='Принимает на себя одну единицу урона от выстрела (удвоенный патрон нанесёт 1 урон), сбрасывается в начале следующего хода',inline=False)
                    embed.add_field(name=f'Наручники ({self.dealer_inv["handcuffs"]} шт.)',value='Пропускает ход оппонента',inline=False)
                    await inter.response.send_message('Что использовать?',embed=embed,view=view,ephemeral=True)
                    message = await inter.original_message()
                    await view.wait()
                    view.clear_items()
                    embed = None
                    if view.value is None:
                        await message.delete()
                    elif self.dealer_inv[view.value] == 0:
                        await message.edit('У вас нет этого предмета.',view=view,embed=embed)
                    else:
                        if view.value == 'glass':
                            await message.edit(f'{self.barrel.count(1)} патрон(а), {self.barrel.count(0)} пустой(-ых)\n\nСейчас заряжен '+('**пустой**.' if self.barrel[0] == 0 else '**патрон**.'),view=view,embed=embed)
                        if view.value == 'beer':
                            self.value = 'Beer'
                            await message.delete()
                            self.stop()
                        if view.value == 'doubler':
                            if self.doubled:
                                await message.edit('Урон уже удвоен!',view=view,embed=embed)
                                self.dealer_inv[view.value] += 1
                                self.dealer_inv['total'] += 1
                            else:
                                self.value = 'Doubler'
                                await message.delete()
                                self.stop()
                        if view.value == 'shield':
                            if self.dealer_inv['shielded']:
                                await message.edit('Вы уже под щитом!',view=view,embed=embed)
                                self.dealer_inv[view.value] += 1
                                self.dealer_inv['total'] += 1
                            else:
                                self.value = 'Shield'
                                await message.delete()
                                self.stop()
                        if view.value == 'handcuffs':
                            if self.handcuffed:
                                await message.edit('Оппонент уже в наручниках!',view=view,embed=embed)
                                self.dealer_inv[view.value] += 1
                                self.dealer_inv['total'] += 1
                            else:
                                self.value = 'Handcuffs'
                                await message.delete()
                                self.stop()
                        self.dealer_inv[view.value] -= 1
                        self.dealer_inv['total'] -= 1

          if inter.user == self.player:
                if self.player_inv['total'] == 0:
                    await inter.response.send_message('Инвентарь пуст, использовать нечего. <:HUH:1187112357541974077>',ephemeral=True)
                else:
                    inv = self.player_inv
                    view = Use()
                    embed = disnake.Embed(color=disnake.Color(0x474896))
                    embed.add_field(name=f'Стекло ({self.player_inv["glass"]} шт.)',value='Отображает кол-во патрон в барабане и **текущий патрон**',inline=False)
                    embed.add_field(name=f'Пиво ({self.player_inv["beer"]} шт.)',value='Сбрасывает текущий патрон, завершает раунд если барабан пустой',inline=False)
                    embed.add_field(name=f'Удвоитель ({self.player_inv["doubler"]} шт.)',value='Удваивает урон на один заряженный выстрел или до конца хода',inline=False)
                    embed.add_field(name=f'Щит ({self.player_inv["shield"]} шт.)',value='Принимает на себя одну единицу урона от выстрела (удвоенный патрон нанесёт 1 урон), сбрасывается в начале следующего хода',inline=False)
                    embed.add_field(name=f'Наручники ({self.player_inv["handcuffs"]} шт.)',value='Пропускает ход оппонента',inline=False)
                    await inter.response.send_message('Что использовать?',embed=embed,view=view,ephemeral=True)
                    message = await inter.original_message()
                    await view.wait()
                    view.clear_items()
                    embed = None
                    if view.value is None:
                        await message.delete()
                    elif self.player_inv[view.value] == 0:
                        await message.edit('У вас нет этого предмета.',view=view,embed=embed)
                    else:
                        if view.value == 'glass':
                            await message.edit(f'{self.barrel.count(1)} патрон(а), {self.barrel.count(0)} пустой(-ых)\n\nСейчас заряжен '+('**пустой**.' if self.barrel[0] == 0 else '**патрон**.'),view=view,embed=embed)
                        if view.value == 'beer':
                            self.value = 'Beer'
                            await message.delete()
                            self.stop()
                        if view.value == 'doubler':
                            if self.doubled:
                                await message.edit('Урон уже удвоен!',view=view,embed=embed)
                                self.player_inv[view.value] += 1
                                self.player_inv['total'] += 1
                            else:
                                self.value = 'Doubler'
                                await message.delete()
                                self.stop()
                        if view.value == 'shield':
                            if self.player_inv['shielded']:
                                await message.edit('Вы уже под щитом!',view=view,embed=embed)
                                self.player_inv[view.value] += 1
                                self.player_inv['total'] += 1
                            else:
                                self.value = 'Shield'
                                await message.delete()
                                self.stop()
                        if view.value == 'handcuffs':
                            if self.handcuffed:
                                await message.edit('Оппонент уже в наручниках!',view=view,embed=embed)
                                self.player_inv[view.value] += 1
                                self.player_inv['total'] += 1
                            else:
                                self.value = 'Handcuffs'
                                await message.delete()
                                self.stop()
                        self.player_inv[view.value] -= 1
                        self.player_inv['total'] -= 1
        else:
            if inter.user == self.dealer:
                embed = disnake.Embed(color=disnake.Color(0x474896))
                embed.add_field(name=f'Стекло ({self.dealer_inv["glass"]} шт.)',value='',inline=False)
                embed.add_field(name=f'Пиво ({self.dealer_inv["beer"]} шт.)',value='',inline=False)
                embed.add_field(name=f'Удвоитель ({self.dealer_inv["doubler"]} шт.)',value='',inline=False)
                embed.add_field(name=f'Щит ({self.dealer_inv["shield"]} шт.)',value='',inline=False)
                embed.add_field(name=f'Наручники ({self.dealer_inv["handcuffs"]} шт.)',value='',inline=False)
                await inter.response.send_message('Сейчас не ваш ход, но на свой инвентарь посмотреть вы можете:',embed=embed,ephemeral=True)
            if inter.user == self.player:
                embed = disnake.Embed(color=disnake.Color(0x474896))
                embed.add_field(name=f'Стекло ({self.player_inv["glass"]} шт.)',value='',inline=False)
                embed.add_field(name=f'Пиво ({self.player_inv["beer"]} шт.)',value='',inline=False)
                embed.add_field(name=f'Удвоитель ({self.player_inv["doubler"]} шт.)',value='',inline=False)
                embed.add_field(name=f'Щит ({self.player_inv["shield"]} шт.)',value='',inline=False)
                embed.add_field(name=f'Наручники ({self.player_inv["handcuffs"]} шт.)',value='',inline=False)
                await inter.response.send_message('Сейчас не ваш ход, но на свой инвентарь посмотреть вы можете:',embed=embed,ephemeral=True)
            else:
                await inter.response.send_message('Вы не участвуете в игре.', ephemeral=True)
       
    @disnake.ui.button(label="Инвентарь оппонента", style=disnake.ButtonStyle.blurple)
    async def inv_opponent(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if inter.user == self.dealer:
            if self.player_inv['total'] == 0:
                await inter.response.send_message('Инвентарь оппонента пуст.',ephemeral=True)
            else:
                embed = disnake.Embed(color=disnake.Color(0x474896))
                embed.add_field(name=f'Стекло ({self.player_inv["glass"]} шт.)',value='',inline=False)
                embed.add_field(name=f'Пиво ({self.player_inv["beer"]} шт.)',value='',inline=False)
                embed.add_field(name=f'Удвоитель ({self.player_inv["doubler"]} шт.)',value='',inline=False)
                embed.add_field(name=f'Щит ({self.player_inv["shield"]} шт.)',value='',inline=False)
                embed.add_field(name=f'Наручники ({self.player_inv["handcuffs"]} шт.)',value='',inline=False)
                await inter.response.send_message('**Инвентарь оппонента:**',embed=embed,ephemeral=True)
        elif inter.user == self.player:
            if self.dealer_inv['total'] == 0:
                await inter.response.send_message('Инвентарь оппонента пуст.',ephemeral=True)
            else:
                embed = disnake.Embed(color=disnake.Color(0x474896))
                embed.add_field(name=f'Стекло ({self.dealer_inv["glass"]} шт.)',value='',inline=False)
                embed.add_field(name=f'Пиво ({self.dealer_inv["beer"]} шт.)',value='',inline=False)
                embed.add_field(name=f'Удвоитель ({self.dealer_inv["doubler"]} шт.)',value='',inline=False)
                embed.add_field(name=f'Щит ({self.dealer_inv["shield"]} шт.)',value='',inline=False)
                embed.add_field(name=f'Наручники ({self.dealer_inv["handcuffs"]} шт.)',value='',inline=False)
                await inter.response.send_message('**Инвентарь оппонента:**',embed=embed,ephemeral=True)
        else:
            await inter.response.send_message('Вы не участвуете в игре.', ephemeral=True)

class Confirm(disnake.ui.View):
    def __init__(self, author, duel_member):
        self.author = author
        self.duel_member = duel_member
        super().__init__(timeout=60.0)
        self.value: Optional[bool] = None
        self.user: Optional[int] = None

    @disnake.ui.button(label="Принять вызов!", style=disnake.ButtonStyle.blurple)
    async def confirm(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if inter.user.id == self.author.id:
          await inter.response.send_message('Нельзя присоединиться к самому себе.', ephemeral=True)
        elif self.duel_member and inter.user != self.duel_member:
            await inter.response.send_message('Вы не можете принять чужой вызов.', ephemeral=True)
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

    async def callback(self, inter: disnake.MessageInteraction):
        if self.question == 1:
            if inter.values[0] == 'q1_a3':
                self.score += 1

            qs = QuestionSelect(question=2)
            qs.score = self.score
            qs.message = self.message
            view = disnake.ui.View()
            view.add_item(qs)
            try:
                await inter.send()
            except Exception:
                pass
            await self.message.edit('Вы видите, что в чате начался сущий кошмар: участники оскорбляют друг друга, матерятся, да и вообще не соблюдают интернет-манеры! \nЧто нужно сделать **в первую очередь**?', view=view)
        elif self.question == 2:
            if inter.values[0] == 'q2_a1':
                self.score += 1

            qs = QuestionSelect(question=3)
            qs.score = self.score
            qs.message = self.message
            view = disnake.ui.View()
            view.add_item(qs)
            try:
                await inter.send()
            except Exception:
                pass
            await self.message.edit('Самое полезное и лучшее правило (по вашему скромному мнению)?', view=view)
        elif self.question == 3:
            if inter.values[0] != 'q3_a1':
                self.score += 1

            try:
                await inter.send()
            except Exception:
                pass

            if self.score >= 2:
                role = inter.guild.get_role(1014569986968268891)
                await inter.author.add_roles(role)
                inter.bot.add_user_to_db(inter.author.id)
                await self.message.edit(':ballot_box_with_check: Поздравляю с прохождением верификации! Теперь ты полноценный член нашего рандомного общества. Приятного общения!', view=None)
            else:
                await self.message.edit(':x: Где-то вы ошиблись. Попробуйте ещё раз. <:nikoeepy:1181309167152136264>', view=None)

def setup(bot: commands.Bot):
    bot.add_cog(Prikol(bot))