import discord
from discord.ext import commands
from collections import defaultdict
from time import monotonic


# ============================================================
# PALABRAS PROHIBIDAS
# ============================================================

PALABRAS_PROHIBIDAS = [
    "spam",
    "hack",
    "hacks",
    "cheat",
    "cheats",
    "aimbot",
    "wallhack",
    "exploit",
    "injector",

    "puta",
    "puto",
    "gilipollas",
    "idiota",
    "imbécil",
    "imbecil",
    "subnormal",
    "cabrón",
    "cabron",
    "mierda",
    "joder",
    "coño",
    "hostia",
    "hijo de puta",
    "hija de puta"
]


# ============================================================
# CONFIGURACIÓN ANTI-SPAM
# ============================================================

MAX_MENSAJES = 5
INTERVALO_SPAM = 5

MAX_MENCIONES = 5


# ============================================================
# AUTOMOD
# ============================================================

class Automod(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        # Mensajes recientes de cada usuario
        self.mensajes_usuario = defaultdict(list)

        print("🟢 Automod.py iniciado")


    # ========================================================
    # ENVIAR LOG
    # ========================================================

    async def enviar_log_automod(
        self,
        message,
        motivo
    ):

        logs = self.bot.get_cog("Logs")

        if logs is None:
            return

        try:

            await logs.automod_log(
                message,
                motivo
            )

        except Exception as error:

            print(
                f"❌ Error enviando log de Automod: {error}"
            )


    # ========================================================
    # AVISO PRIVADO AL USUARIO
    # ========================================================

    async def enviar_aviso_privado(
        self,
        message,
        texto
    ):

        try:

            embed = discord.Embed(
                title="⚠️ Automoderación",
                description=texto,
                color=discord.Color.orange()
            )

            embed.add_field(
                name="📍 Canal",
                value=message.channel.mention,
                inline=True
            )

            embed.set_footer(
                text="The Warriors • Automod"
            )

            await message.author.send(
                embed=embed
            )

        except discord.Forbidden:

            # El usuario puede tener los MD cerrados.
            pass

        except discord.HTTPException:

            pass


    # ========================================================
    # BORRAR MENSAJE
    # ========================================================

    async def borrar_mensaje(
        self,
        message
    ):

        try:

            await message.delete()

            return True

        except discord.NotFound:

            return True

        except discord.Forbidden:

            print(
                "❌ Automod no tiene permiso para borrar mensajes."
            )

            return False

        except discord.HTTPException as error:

            print(
                f"❌ Error borrando mensaje: {error}"
            )

            return False


    # ========================================================
    # DETECTAR MENSAJES
    # ========================================================

    @commands.Cog.listener()
    async def on_message(
        self,
        message
    ):

        # ====================================================
        # IGNORAR BOTS
        # ====================================================

        if message.author.bot:
            return


        # ====================================================
        # IGNORAR MENSAJES PRIVADOS
        # ====================================================

        if message.guild is None:
            return


        # ====================================================
        # MODERADORES PUEDEN SALTARSE AUTOMOD
        # ====================================================

        if message.author.guild_permissions.manage_messages:
            return


        contenido = message.content.lower()


        # ====================================================
        # ANTI-SPAM
        # ====================================================

        ahora = monotonic()

        clave_usuario = (
            message.guild.id,
            message.author.id
        )

        mensajes = self.mensajes_usuario[
            clave_usuario
        ]

        mensajes[:] = [
            tiempo
            for tiempo in mensajes
            if ahora - tiempo <= INTERVALO_SPAM
        ]

        mensajes.append(ahora)


        if len(mensajes) >= MAX_MENSAJES:

            eliminado = await self.borrar_mensaje(
                message
            )

            if eliminado:

                await self.enviar_log_automod(
                    message,
                    "Spam: demasiados mensajes en poco tiempo"
                )

                await self.enviar_aviso_privado(
                    message,
                    "Has enviado demasiados mensajes "
                    "en poco tiempo.\n\n"
                    "🗑️ Tu mensaje ha sido eliminado."
                )

            mensajes.clear()

            return


        # ====================================================
        # ENLACES / INVITACIONES
        # ====================================================

        contiene_enlace = (
            "http://" in contenido
            or "https://" in contenido
            or "www." in contenido
            or "discord.gg/" in contenido
            or "discord.com/invite/" in contenido
            or "discordapp.com/invite/" in contenido
        )


        if contiene_enlace:

            eliminado = await self.borrar_mensaje(
                message
            )

            if eliminado:

                await self.enviar_log_automod(
                    message,
                    "Enlace o invitación no permitida"
                )

                await self.enviar_aviso_privado(
                    message,
                    "No puedes enviar enlaces "
                    "o invitaciones en este servidor.\n\n"
                    "🗑️ Tu mensaje ha sido eliminado."
                )

            return


        # ====================================================
        # PALABRAS PROHIBIDAS
        # ====================================================

        for palabra in PALABRAS_PROHIBIDAS:

            if palabra in contenido:

                eliminado = await self.borrar_mensaje(
                    message
                )

                if eliminado:

                    await self.enviar_log_automod(
                        message,
                        f"Palabra prohibida: {palabra}"
                    )

                    await self.enviar_aviso_privado(
                        message,
                        "Ese mensaje contiene una "
                        "palabra prohibida.\n\n"
                        "🗑️ Tu mensaje ha sido eliminado."
                    )

                return


        # ====================================================
        # EXCESO DE MENCIONES
        # ====================================================

        if len(message.mentions) >= MAX_MENCIONES:

            eliminado = await self.borrar_mensaje(
                message
            )

            if eliminado:

                await self.enviar_log_automod(
                    message,
                    "Demasiadas menciones"
                )

                await self.enviar_aviso_privado(
                    message,
                    "Has mencionado a demasiados usuarios "
                    "en un mismo mensaje.\n\n"
                    "🗑️ Tu mensaje ha sido eliminado."
                )

            return


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        Automod(bot)
    )

    print(
        "✅ Automod cargado correctamente."
    )
