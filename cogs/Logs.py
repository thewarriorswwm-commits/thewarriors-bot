import discord
from discord.ext import commands
import asyncio


# ============================================================
# CONFIGURACIÓN
# ============================================================

CANAL_LOGS = "logs-📋"


# ============================================================
# COG LOGS
# ============================================================

class Logs(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        print("🟢 Logs.py iniciado")

    # ========================================================
    # ENVIAR LOG
    # ========================================================

    async def enviar_log(
        self,
        guild,
        titulo,
        descripcion,
        color=discord.Color.blue()
    ):

        if guild is None:
            return

        canal = discord.utils.get(
            guild.text_channels,
            name=CANAL_LOGS
        )

        if canal is None:
            print(
                f"⚠️ No encuentro #{CANAL_LOGS} "
                f"en {guild.name}"
            )
            return

        embed = discord.Embed(
            title=titulo,
            description=descripcion,
            color=color,
            timestamp=discord.utils.utcnow()
        )

        embed.set_footer(
            text="The Warriors • Sistema de logs"
        )

        try:

            await canal.send(
                embed=embed
            )

        except discord.Forbidden:

            print(
                "❌ No puedo escribir en #logs-📋."
            )

        except discord.HTTPException as error:

            print(
                f"❌ Error enviando log: {error}"
            )

    # ========================================================
    # BUSCAR MODERADOR EN AUDIT LOG
    # ========================================================

    async def buscar_moderador(
        self,
        guild,
        accion,
        objetivo_id
    ):

        try:

            async for entrada in guild.audit_logs(
                limit=10,
                action=accion
            ):

                if entrada.target and getattr(
                    entrada.target,
                    "id",
                    None
                ) == objetivo_id:

                    return entrada.user

        except discord.Forbidden:

            print(
                "⚠️ No tengo permiso para ver "
                "el registro de auditoría."
            )

        except discord.HTTPException as error:

            print(
                f"⚠️ Error leyendo Audit Log: {error}"
            )

        return None

    # ========================================================
    # AUTOMOD
    # ========================================================

    async def automod_log(
        self,
        message,
        motivo
    ):

        if message.guild is None:
            return

        contenido = message.content

        if not contenido:
            contenido = "*Sin contenido de texto*"

        await self.enviar_log(

            message.guild,

            "🛡️ Automod",

            (
                f"👤 **Usuario:** "
                f"{message.author.mention}\n"

                f"📍 **Canal:** "
                f"{message.channel.mention}\n"

                f"⚠️ **Motivo:** "
                f"{motivo}\n\n"

                f"💬 **Mensaje:**\n"
                f"{contenido[:1000]}"
            ),

            discord.Color.orange()
        )

    # ========================================================
    # ENTRA MIEMBRO
    # ========================================================

    @commands.Cog.listener()
    async def on_member_join(
        self,
        member
    ):

        await self.enviar_log(

            member.guild,

            "📥 Usuario entrante",

            (
                f"👤 **Usuario:** "
                f"{member.mention}\n"

                f"🆔 **ID:** "
                f"`{member.id}`"
            ),

            discord.Color.green()
        )

    # ========================================================
    # SALE MIEMBRO
    # ========================================================

    @commands.Cog.listener()
    async def on_member_remove(
        self,
        member
    ):

        await self.enviar_log(

            member.guild,

            "📤 Usuario salido",

            (
                f"👤 **Usuario:** "
                f"{member}\n"

                f"🆔 **ID:** "
                f"`{member.id}`"
            ),

            discord.Color.red()
        )

    # ========================================================
    # MENSAJE ELIMINADO
    # ========================================================

    @commands.Cog.listener()
    async def on_message_delete(
        self,
        message
    ):

        if message.author.bot:
            return

        if message.guild is None:
            return

        contenido = message.content

        if not contenido:
            contenido = "*Sin contenido de texto*"

        await self.enviar_log(

            message.guild,

            "🗑️ Mensaje eliminado",

            (
                f"👤 **Autor:** "
                f"{message.author.mention}\n"

                f"📍 **Canal:** "
                f"{message.channel.mention}\n\n"

                f"💬 **Contenido:**\n"
                f"{contenido[:1000]}"
            ),

            discord.Color.red()
        )

    # ========================================================
    # MENSAJE EDITADO
    # ========================================================

    @commands.Cog.listener()
    async def on_message_edit(
        self,
        before,
        after
    ):

        if before.author.bot:
            return

        if before.guild is None:
            return

        if before.content == after.content:
            return

        await self.enviar_log(

            before.guild,

            "✏️ Mensaje editado",

            (
                f"👤 **Autor:** "
                f"{before.author.mention}\n"

                f"📍 **Canal:** "
                f"{before.channel.mention}\n\n"

                f"🔴 **Antes:**\n"
                f"{before.content[:500]}\n\n"

                f"🟢 **Después:**\n"
                f"{after.content[:500]}"
            ),

            discord.Color.yellow()
        )

    # ========================================================
    # CAMBIO DE ROLES
    # ========================================================

    @commands.Cog.listener()
    async def on_member_update(
        self,
        before,
        after
    ):

        roles_antes = set(
            before.roles
        )

        roles_despues = set(
            after.roles
        )

        añadidos = (
            roles_despues - roles_antes
        )

        eliminados = (
            roles_antes - roles_despues
        )

        if not añadidos and not eliminados:
            return

        texto = (
            f"👤 **Usuario:** "
            f"{after.mention}\n\n"
        )

        if añadidos:

            texto += (
                "➕ **Roles añadidos:**\n"
                + ", ".join(
                    role.mention
                    for role in añadidos
                )
                + "\n\n"
            )

        if eliminados:

            texto += (
                "➖ **Roles eliminados:**\n"
                + ", ".join(
                    role.mention
                    for role in eliminados
                )
            )

        await self.enviar_log(

            after.guild,

            "🎭 Cambio de roles",

            texto,

            discord.Color.purple()
        )

    # ========================================================
    # BAN
    # ========================================================

    @commands.Cog.listener()
    async def on_member_ban(
        self,
        guild,
        user
    ):

        await asyncio.sleep(1)

        moderador = await self.buscar_moderador(
            guild,
            discord.AuditLogAction.ban,
            user.id
        )

        if moderador:

            quien = moderador.mention

        else:

            quien = "*No identificado*"

        await self.enviar_log(

            guild,

            "🔨 Usuario baneado",

            (
                f"👤 **Usuario baneado:** "
                f"{user}\n"

                f"🆔 **ID:** "
                f"`{user.id}`\n\n"

                f"🛡️ **Moderador:** "
                f"{quien}"
            ),

            discord.Color.dark_red()
        )

    # ========================================================
    # DESBAN
    # ========================================================

    @commands.Cog.listener()
    async def on_member_unban(
        self,
        guild,
        user
    ):

        await asyncio.sleep(1)

        moderador = await self.buscar_moderador(
            guild,
            discord.AuditLogAction.unban,
            user.id
        )

        if moderador:

            quien = moderador.mention

        else:

            quien = "*No identificado*"

        await self.enviar_log(

            guild,

            "🔓 Usuario desbaneado",

            (
                f"👤 **Usuario:** "
                f"{user}\n"

                f"🆔 **ID:** "
                f"`{user.id}`\n\n"

                f"🛡️ **Moderador:** "
                f"{quien}"
            ),

            discord.Color.green()
        )


# ============================================================
# SETUP
# ============================================================

async def setup(
    bot
):

    await bot.add_cog(
        Logs(bot)
    )

    print(
        "✅ Logs.py cargado correctamente."
    )