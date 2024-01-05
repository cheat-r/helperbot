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

def setup(bot: commands.Bot):
    bot.add_cog(Experimental(bot))