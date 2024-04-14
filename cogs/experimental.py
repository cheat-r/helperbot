import disnake
from disnake.ext import commands

class Experimental(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    def cog_load(self):
        print('Ког загружен: "{}"'.format(self.qualified_name))
    def cog_unload(self):
        print('Ког выгружен: "{}"'.format(self.qualified_name))

    @commands.slash_command(description='Пересылает желаемый эмодзи с сервера через бота', options=[
    disnake.Option('name', 'Название эмодзи', disnake.OptionType.string, required=True)])
    async def emoji(self, inter: disnake.ApplicationCommandInteraction, name: str):
        await inter.response.defer(ephemeral=True)
        emote = disnake.utils.get(inter.guild.emojis, name=name)
        if emote == None:
            if name.startswith('<') or name.startswith(':'):
                await inter.edit_original_response('Вставка эмодзи напрямую *пока* не работает. Попробуйте ещё раз, написав название эмодзи.')
            else:
                await inter.edit_original_response('Эмодзи не найден. Проверьте правильность написания (в том числе заглавные буквы) и попробуйте ещё раз.')
        else:
            await inter.channel.send(emote)
            await inter.edit_original_response('Эмодзи отправлен.')
    
    @commands.slash_command(description="Управление вашей кастомной ролью", options=[
        disnake.Option('name', 'Название роли', disnake.OptionType.string, required=False),
        disnake.Option('color', 'Цвет в формате #000000, без решётки', disnake.OptionType.string, required=False),
        disnake.Option('mentionable', 'Разрешение на упоминание роли', disnake.OptionType.boolean, required=False),
        disnake.Option('icon', 'Иконка роли (если хватает бустов)', disnake.OptionType.attachment, required=False)
    ])
    async def customrole(self, inter: disnake.ApplicationCommandInteraction, name: str=None, color: str=None, mentionable: bool=None, icon: disnake.Attachment=None):
        embed = disnake.Embed(color=disnake.Color(0x474896))
        dbrole = self.bot.db['members'][str(inter.author.id)]['role']
        if not(name or color or mentionable != None or icon) or dbrole['expired']:
            embed.title = 'Управление ролью'
            if dbrole['id']:
                role = inter.guild.get_role(int(dbrole['id']))
                if dbrole['expired']:
                    embed.add_field(name=f'Истекает:', value=f'**Истёк оплаченный срок!** Роль будет удалена <t:{dbrole["ts"]}:R>', inline=False)
                else:
                    embed.add_field(name=f'Истекает:', value=f'<t:{dbrole["ts"]}:R>', inline=False)
                embed.add_field(name='Название',value=f'{role.name}')
                if str(role.color) == '#000000':
                    embed.add_field(name='Цвет',value='Не установлен')
                else:
                    embed.add_field(name='Цвет',value=f'`{str(role.color)}`')
                    embed.color = role.color
                embed.add_field(name='Пингуемая?',value='✅' if role.mentionable else '❌')
                embed.add_field(name='Иконка',value='Не хватает бустов :(' if role.guild.premium_tier<2 else f'[(просмотреть в браузере)]({role.icon.url})' if role.icon else 'Не установлена')
            else:
                embed.add_field(name='У вас нет кастомной роли!', value='Хотя это поправимо. Купи (или выиграй) сертификат на кастомную роль и используй её.\n(`/shop`)', inline=False)
            await inter.response.send_message(embed=embed,ephemeral=True)
        else:
            if not dbrole['id']:
                await inter.response.send_message('У вас нет кастомной роли! Приобретите её в магазине, после чего возвращайтесь сюда. :)',ephemeral=True)
            elif dbrole['expired']:
                await inter.response.send_message('Ваша кастомная роль просрочена! Пожалуйста, продлите её действие, использовав талон на кастомную роль, после чего попробуйте ещё раз.',ephemeral=True)
            else:
                role = inter.guild.get_role(int(dbrole['id']))
                if name:
                    await role.edit(name=name)
                    embed.add_field(name='Название',value=name)
                if color:
                    try:
                        await role.edit(color=disnake.Color(int(color, 16)))
                        embed.add_field(name='Цвет',value=f'`#{str(color)}`')
                    except:
                        embed.add_field(name='Цвет',value='Hex-код указан некорректно! Попробуйте ещё раз.')
                if mentionable != None:
                    await role.edit(mentionable=mentionable)
                    embed.add_field(name='Пингуемая?',value='✅' if mentionable else '❌')
                if icon:
                    if role.guild.premium_tier < 2:
                        embed.add_field(name='Иконка',value='Не хватает бустов :(')
                    else:
                        try:
                            await role.edit(icon=icon)
                            embed.add_field(name='Иконка',value=f'[(просмотреть в браузере)]({role.icon.url})')
                        except:
                            embed.add_field(name='Иконка',value='Ошибка при смене иконки! Возможно, вы выбрали неправильный формат?')
                await inter.response.send_message('Роль изменена.',embed=embed, ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(Experimental(bot))