import discord
from discord.ext import commands
from datetime import timedelta


# ============================================================
# CONFIGURACIÓN
# ============================================================

CANAL_NORMAS = "normas"


# ============================================================
# COG MODERACIÓN
# ============================================================

class Moderacion(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        print("🟢 Moderacion.py iniciado")


    # ========================================================
    # BAN
    # ========================================================

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(
        self,
        ctx,
        miembro: discord.Member,
        *,
        razon: str = "Sin especificar"
    ):

        if miembro == ctx.author:
            await ctx.send(
                "❌ No puedes banearte a ti mismo.",
                delete_after=5
            )
            return

        if miembro == ctx.guild.owner:
            await ctx.send(
                "❌ No puedes banear al propietario.",
                delete_after=5
            )
            return

        if miembro.top_role >= ctx.author.top_role:
            await ctx.send(
                "❌ No puedes banear a alguien con un rol "
                "igual o superior al tuyo.",
                delete_after=5
            )
            return

        if ctx.guild.me and miembro.top_role >= ctx.guild.me.top_role:
            await ctx.send(
                "❌ Mi rol está por debajo del usuario.",
                delete_after=5
            )
            return

        try:

            await miembro.ban(
                reason=f"{ctx.author}: {razon}"
            )

            await ctx.send(
                f"🔨 **{miembro}** ha sido baneado.\n"
                f"📝 Motivo: **{razon}**"
            )

        except discord.Forbidden:

            await ctx.send(
                "❌ No puedo banear a ese usuario.",
                delete_after=5
            )

        except discord.HTTPException:

            await ctx.send(
                "❌ Discord no ha podido realizar el baneo.",
                delete_after=5
            )


    # ========================================================
    # KICK
    # ========================================================

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(
        self,
        ctx,
        miembro: discord.Member,
        *,
        razon: str = "Sin especificar"
    ):

        if miembro == ctx.author:
            await ctx.send(
                "❌ No puedes expulsarte a ti mismo.",
                delete_after=5
            )
            return

        if miembro == ctx.guild.owner:
            await ctx.send(
                "❌ No puedes expulsar al propietario.",
                delete_after=5
            )
            return

        if miembro.top_role >= ctx.author.top_role:
            await ctx.send(
                "❌ No puedes expulsar a alguien con un rol "
                "igual o superior al tuyo.",
                delete_after=5
            )
            return

        if ctx.guild.me and miembro.top_role >= ctx.guild.me.top_role:
            await ctx.send(
                "❌ Mi rol está por debajo del usuario.",
                delete_after=5
            )
            return

        try:

            await miembro.kick(
                reason=f"{ctx.author}: {razon}"
            )

            await ctx.send(
                f"👢 **{miembro}** ha sido expulsado.\n"
                f"📝 Motivo: **{razon}**"
            )

        except discord.Forbidden:

            await ctx.send(
                "❌ No puedo expulsar a ese usuario.",
                delete_after=5
            )

        except discord.HTTPException:

            await ctx.send(
                "❌ Discord no ha podido realizar la expulsión.",
                delete_after=5
            )


    # ========================================================
    # TIMEOUT
    # ========================================================

    @commands.command(name="timeout")
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def timeout(
        self,
        ctx,
        miembro: discord.Member,
        minutos: int,
        *,
        razon: str = "Sin especificar"
    ):

        if minutos < 1 or minutos > 40320:

            await ctx.send(
                "❌ El timeout debe estar entre "
                "1 minuto y 28 días.",
                delete_after=5
            )

            return

        if miembro == ctx.author:

            await ctx.send(
                "❌ No puedes ponerte timeout a ti mismo.",
                delete_after=5
            )

            return

        if miembro == ctx.guild.owner:

            await ctx.send(
                "❌ No puedes poner timeout al propietario.",
                delete_after=5
            )

            return

        if miembro.top_role >= ctx.author.top_role:

            await ctx.send(
                "❌ No puedes poner timeout a alguien con "
                "un rol igual o superior al tuyo.",
                delete_after=5
            )

            return

        if ctx.guild.me and miembro.top_role >= ctx.guild.me.top_role:

            await ctx.send(
                "❌ Mi rol está por debajo del usuario.",
                delete_after=5
            )

            return

        try:

            await miembro.timeout(
                discord.utils.utcnow()
                + timedelta(minutes=minutos),
                reason=f"{ctx.author}: {razon}"
            )

            await ctx.send(
                f"🔇 **{miembro}** ha recibido timeout durante "
                f"**{minutos} minutos**.\n"
                f"📝 Motivo: **{razon}**"
            )

        except discord.Forbidden:

            await ctx.send(
                "❌ No puedo poner timeout a ese usuario.",
                delete_after=5
            )

        except discord.HTTPException:

            await ctx.send(
                "❌ Discord no ha podido aplicar el timeout.",
                delete_after=5
            )


    # ========================================================
    # WARN
    # ========================================================

    @commands.command(name="warn")
    @commands.has_permissions(moderate_members=True)
    async def warn(
        self,
        ctx,
        miembro: discord.Member,
        *,
        razon: str = "Sin especificar"
    ):

        if miembro == ctx.author:

            await ctx.send(
                "❌ No puedes advertirte a ti mismo.",
                delete_after=5
            )

            return

        if miembro == ctx.guild.owner:

            await ctx.send(
                "❌ No puedes advertir al propietario.",
                delete_after=5
            )

            return

        if miembro.top_role >= ctx.author.top_role:

            await ctx.send(
                "❌ No puedes advertir a alguien con un "
                "rol igual o superior al tuyo.",
                delete_after=5
            )

            return

        await ctx.send(
            f"⚠️ **{miembro.mention}** ha recibido una advertencia.\n"
            f"📝 Motivo: **{razon}**"
        )


    # ========================================================
    # LOCK
    # ========================================================

    @commands.command(name="lock")
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def lock(self, ctx):

        await ctx.channel.set_permissions(
            ctx.guild.default_role,
            send_messages=False
        )

        await ctx.send(
            "🔒 **Canal bloqueado.**"
        )


    # ========================================================
    # UNLOCK
    # ========================================================

    @commands.command(name="unlock")
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def unlock(self, ctx):

        await ctx.channel.set_permissions(
            ctx.guild.default_role,
            send_messages=None
        )

        await ctx.send(
            "🔓 **Canal desbloqueado.**"
        )


    # ========================================================
    # SLOWMODE
    # ========================================================

    @commands.command(name="slowmode")
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def slowmode(
        self,
        ctx,
        segundos: int
    ):

        if segundos < 0 or segundos > 21600:

            await ctx.send(
                "❌ El valor debe estar entre "
                "0 y 21600 segundos.",
                delete_after=5
            )

            return

        try:

            await ctx.channel.edit(
                slowmode_delay=segundos
            )

            if segundos == 0:

                await ctx.send(
                    "⚡ **Slowmode desactivado.**"
                )

            else:

                await ctx.send(
                    f"🐌 Slowmode establecido en "
                    f"**{segundos} segundos**."
                )

        except discord.Forbidden:

            await ctx.send(
                "❌ No puedo modificar el slowmode.",
                delete_after=5
            )


    # ========================================================
    # QUITAR CANDADO DE NORMAS
    # ========================================================

    @commands.command(name="quitarcandadonormas")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def quitarcandadonormas(self, ctx):

        guild = ctx.guild

        canal_normas = discord.utils.get(
            guild.text_channels,
            name=CANAL_NORMAS
        )

        if canal_normas is None:

            await ctx.send(
                "❌ No encuentro el canal **#normas**.",
                delete_after=5
            )

            return

        try:

            await canal_normas.set_permissions(
                guild.default_role,
                view_channel=True,
                read_message_history=True,
                send_messages=False,
                reason="Quitar candado de #normas"
            )

            categoria = canal_normas.category

            if categoria is not None:

                await categoria.set_permissions(
                    guild.default_role,
                    view_channel=True,
                    reason="Quitar candado de categoría de #normas"
                )

            await ctx.send(
                "✅ **Candado de #normas eliminado.**\n\n"
                "👥 @everyone → puede ver #normas.\n"
                "🚫 @everyone → no puede escribir.\n"
                "📖 El canal queda en solo lectura."
            )

        except discord.Forbidden:

            await ctx.send(
                "❌ No tengo permiso para modificar #normas.\n\n"
                "Necesito **Gestionar canales**."
            )

        except discord.HTTPException as error:

            print(
                f"❌ Error quitando candado de normas: {error}"
            )

            await ctx.send(
                "❌ Discord no ha permitido modificar #normas."
            )


# ============================================================
# ERRORES
# ============================================================

    @ban.error
    @kick.error
    @timeout.error
    @warn.error
    @lock.error
    @unlock.error
    @slowmode.error
    @quitarcandadonormas.error
    async def moderacion_error(
        self,
        ctx,
        error
    ):

        if isinstance(
            error,
            commands.MissingPermissions
        ):

            await ctx.send(
                "❌ No tienes permisos para utilizar "
                "este comando.",
                delete_after=5
            )

        elif isinstance(
            error,
            commands.BotMissingPermissions
        ):

            await ctx.send(
                "❌ Al bot le faltan permisos.",
                delete_after=5
            )

        elif isinstance(
            error,
            commands.MissingRequiredArgument
        ):

            await ctx.send(
                "❌ Faltan argumentos.",
                delete_after=5
            )

        elif isinstance(
            error,
            commands.BadArgument
        ):

            await ctx.send(
                "❌ El valor introducido no es válido.",
                delete_after=5
            )

        else:

            print(
                f"❌ Error en Moderacion.py: {error}"
            )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    if bot.get_cog("Moderacion") is not None:

        print(
            "⚠️ Moderacion ya estaba cargado."
        )

        return

    await bot.add_cog(
        Moderacion(bot)
    )

    print(
        "✅ Moderacion.py cargado correctamente."
    )
