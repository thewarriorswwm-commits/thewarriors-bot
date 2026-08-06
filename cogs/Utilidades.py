import discord
from discord import app_commands
from discord.ext import commands


# ============================================================
# CONFIGURACIÓN
# ============================================================

CANAL_UTILIDADES = "utilidades-🛠️"


# ============================================================
# VISTA DEL PANEL
# ============================================================

class UtilidadesView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)


    # ========================================================
    # BOTÓN AYUDA
    # ========================================================

    @discord.ui.button(
        label="Ayuda",
        emoji="📖",
        style=discord.ButtonStyle.primary,
        custom_id="utilidades_ayuda"
    )
    async def ayuda(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = discord.Embed(
            title="📖 Ayuda",
            description=(
                "Estos son los comandos disponibles "
                "para los miembros."
            ),
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="🛠️ Utilidades",
            value=(
                "`/ping` — Latencia del bot.\n"
                "`/avatar` — Avatar de un usuario.\n"
                "`/userinfo` — Información de un usuario.\n"
                "`/serverinfo` — Información del servidor.\n"
                "`/roles` — Roles del servidor.\n"
                "`/canales` — Canales del servidor."
            ),
            inline=False
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


# ============================================================
# COG UTILIDADES
# ============================================================

class Utilidades(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        print("🟢 Utilidades.py iniciado")


    # ========================================================
    # PANEL AUTOMÁTICO
    # ========================================================

    @commands.Cog.listener()
    async def on_ready(self):

        canal = discord.utils.get(
            self.bot.get_all_channels(),
            name=CANAL_UTILIDADES
        )

        if canal is None:

            print(
                f"⚠️ No encuentro el canal #{CANAL_UTILIDADES}"
            )

            return

        # Evitar enviar el panel varias veces
        async for mensaje in canal.history(limit=50):

            if (
                mensaje.author == self.bot.user
                and mensaje.embeds
                and mensaje.embeds[0].title
                == "🛠️ Panel de Utilidades"
            ):

                print(
                    "✅ Panel de Utilidades ya existe."
                )

                return

        embed = discord.Embed(
            title="🛠️ Panel de Utilidades",
            description=(
                "Bienvenido al panel de utilidades de "
                "**The Warriors**.\n\n"
                "Utiliza los comandos `/` disponibles "
                "para consultar información del servidor "
                "y del bot."
            ),
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="👥 Para miembros",
            value=(
                "`/ping`\n"
                "`/avatar`\n"
                "`/userinfo`\n"
                "`/serverinfo`\n"
                "`/roles`\n"
                "`/canales`\n"
                "`/ayuda`"
            ),
            inline=False
        )

        embed.add_field(
            name="🛡️ Para administradores",
            value=(
                "Los comandos administrativos están "
                "protegidos y no aparecen para miembros "
                "sin permisos."
            ),
            inline=False
        )

        embed.set_footer(
            text="The Warriors • Utilidades"
        )

        try:

            await canal.send(
                embed=embed,
                view=UtilidadesView()
            )

            print(
                "✅ Panel de Utilidades enviado."
            )

        except discord.Forbidden:

            print(
                "❌ No tengo permisos para enviar "
                "el panel en #utilidades-🛠️."
            )

        except discord.HTTPException as error:

            print(
                f"❌ Error enviando panel: {error}"
            )


    # ========================================================
    # PING
    # ========================================================

    @commands.hybrid_command(
        name="ping",
        description="Comprueba la latencia del bot."
    )
    async def ping(self, ctx):

        latencia = round(
            self.bot.latency * 1000
        )

        await ctx.send(
            f"🏓 **Pong!**\n"
            f"📡 Latencia: **{latencia} ms**",
            ephemeral=True
        )


    # ========================================================
    # AVATAR
    # ========================================================

    @commands.hybrid_command(
        name="avatar",
        description="Muestra el avatar de un usuario."
    )
    async def avatar(
        self,
        ctx,
        usuario: discord.Member = None
    ):

        usuario = usuario or ctx.author

        embed = discord.Embed(
            title=f"🖼️ Avatar de {usuario.display_name}",
            color=discord.Color.blurple()
        )

        embed.set_image(
            url=usuario.display_avatar.url
        )

        await ctx.send(
            embed=embed,
            ephemeral=True
        )


    # ========================================================
    # USERINFO
    # ========================================================

    @commands.hybrid_command(
        name="userinfo",
        description="Muestra información de un usuario."
    )
    async def userinfo(
        self,
        ctx,
        usuario: discord.Member = None
    ):

        usuario = usuario or ctx.author

        embed = discord.Embed(
            title="👤 Información del usuario",
            color=discord.Color.blurple()
        )

        embed.set_thumbnail(
            url=usuario.display_avatar.url
        )

        embed.add_field(
            name="👤 Usuario",
            value=usuario.mention,
            inline=True
        )

        embed.add_field(
            name="🆔 ID",
            value=str(usuario.id),
            inline=True
        )

        embed.add_field(
            name="🏷️ Apodo",
            value=usuario.display_name,
            inline=True
        )

        embed.add_field(
            name="📅 Cuenta creada",
            value=discord.utils.format_dt(
                usuario.created_at,
                style="F"
            ),
            inline=False
        )

        if usuario.joined_at:

            embed.add_field(
                name="📥 Entró al servidor",
                value=discord.utils.format_dt(
                    usuario.joined_at,
                    style="F"
                ),
                inline=False
            )

        embed.add_field(
            name="🎭 Roles",
            value=str(
                max(0, len(usuario.roles) - 1)
            ),
            inline=True
        )

        await ctx.send(
            embed=embed,
            ephemeral=True
        )


    # ========================================================
    # SERVERINFO
    # ========================================================

    @commands.hybrid_command(
        name="serverinfo",
        description="Muestra información del servidor."
    )
    async def serverinfo(self, ctx):

        guild = ctx.guild

        if guild is None:

            await ctx.send(
                "❌ Solo puede utilizarse "
                "en un servidor.",
                ephemeral=True
            )

            return

        embed = discord.Embed(
            title=f"🛡️ {guild.name}",
            color=discord.Color.blurple()
        )

        if guild.icon:

            embed.set_thumbnail(
                url=guild.icon.url
            )

        embed.add_field(
            name="👑 Propietario",
            value=(
                guild.owner.mention
                if guild.owner
                else "Desconocido"
            ),
            inline=True
        )

        embed.add_field(
            name="👥 Miembros",
            value=str(guild.member_count),
            inline=True
        )

        embed.add_field(
            name="💬 Canales",
            value=str(len(guild.channels)),
            inline=True
        )

        embed.add_field(
            name="🎭 Roles",
            value=str(len(guild.roles)),
            inline=True
        )

        embed.add_field(
            name="🆔 ID",
            value=str(guild.id),
            inline=True
        )

        embed.add_field(
            name="📅 Creado",
            value=discord.utils.format_dt(
                guild.created_at,
                style="F"
            ),
            inline=False
        )

        await ctx.send(
            embed=embed,
            ephemeral=True
        )


    # ========================================================
    # BOTINFO — SOLO ADMINISTRADORES
    # ========================================================

    @commands.hybrid_command(
        name="botinfo",
        description="Muestra información del bot."
    )
    @app_commands.default_permissions(
        administrator=True
    )
    @commands.has_permissions(
        administrator=True
    )
    async def botinfo(self, ctx):

        embed = discord.Embed(
            title="🤖 Información del bot",
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="🤖 Nombre",
            value=self.bot.user.name,
            inline=True
        )

        embed.add_field(
            name="🆔 ID",
            value=str(self.bot.user.id),
            inline=True
        )

        embed.add_field(
            name="📡 Latencia",
            value=f"{round(self.bot.latency * 1000)} ms",
            inline=True
        )

        embed.add_field(
            name="🧩 Módulos",
            value=str(len(self.bot.cogs)),
            inline=True
        )

        embed.add_field(
            name="👥 Servidores",
            value=str(len(self.bot.guilds)),
            inline=True
        )

        await ctx.send(
            embed=embed,
            ephemeral=True
        )


    # ========================================================
    # ROLES
    # ========================================================

    @commands.hybrid_command(
        name="roles",
        description="Muestra los roles del servidor."
    )
    async def roles(self, ctx):

        if ctx.guild is None:

            await ctx.send(
                "❌ Solo puede utilizarse "
                "en un servidor.",
                ephemeral=True
            )

            return

        roles = [
            role.mention
            for role in ctx.guild.roles
            if role.name != "@everyone"
        ]

        texto = (
            "\n".join(roles)
            if roles
            else "No hay roles disponibles."
        )

        if len(texto) > 1900:

            texto = texto[:1900] + "\n..."

        embed = discord.Embed(
            title="🎭 Roles del servidor",
            description=texto,
            color=discord.Color.blurple()
        )

        await ctx.send(
            embed=embed,
            ephemeral=True
        )


    # ========================================================
    # CANALES
    # ========================================================

    @commands.hybrid_command(
        name="canales",
        description="Muestra los canales del servidor."
    )
    async def canales(self, ctx):

        if ctx.guild is None:

            await ctx.send(
                "❌ Solo puede utilizarse "
                "en un servidor.",
                ephemeral=True
            )

            return

        categorias = {}
        sin_categoria = []

        for canal in ctx.guild.channels:

            if isinstance(
                canal,
                discord.CategoryChannel
            ):
                continue

            if canal.category:

                categorias.setdefault(
                    canal.category.name,
                    []
                ).append(canal)

            else:

                sin_categoria.append(canal)

        descripcion = ""

        for categoria, canales in categorias.items():

            descripcion += (
                f"\n**📁 {categoria}**\n"
            )

            for canal in canales:

                if isinstance(
                    canal,
                    discord.TextChannel
                ):

                    descripcion += (
                        f"💬 {canal.mention}\n"
                    )

                elif isinstance(
                    canal,
                    discord.VoiceChannel
                ):

                    descripcion += (
                        f"🔊 **{canal.name}**\n"
                    )

        if sin_categoria:

            descripcion += (
                "\n**📂 Sin categoría**\n"
            )

            for canal in sin_categoria:

                if isinstance(
                    canal,
                    discord.TextChannel
                ):

                    descripcion += (
                        f"💬 {canal.mention}\n"
                    )

                elif isinstance(
                    canal,
                    discord.VoiceChannel
                ):

                    descripcion += (
                        f"🔊 **{canal.name}**\n"
                    )

        if len(descripcion) > 4000:

            descripcion = descripcion[:3990] + "\n..."

        embed = discord.Embed(
            title="📚 Canales del servidor",
            description=descripcion,
            color=discord.Color.blurple()
        )

        await ctx.send(
            embed=embed,
            ephemeral=True
        )


    # ========================================================
    # AYUDA
    # ========================================================

    @commands.hybrid_command(
        name="ayuda",
        description="Muestra los comandos disponibles."
    )
    async def ayuda(self, ctx):

        embed = discord.Embed(
            title="📖 Ayuda del bot",
            description=(
                "Estos son los comandos disponibles "
                "para los miembros."
            ),
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="🛠️ Utilidades",
            value=(
                "`/ping`\n"
                "`/avatar`\n"
                "`/userinfo`\n"
                "`/serverinfo`\n"
                "`/roles`\n"
                "`/canales`"
            ),
            inline=False
        )

        embed.add_field(
            name="🛡️ Administradores",
            value=(
                "Los comandos administrativos están "
                "protegidos y no aparecen para usuarios "
                "sin permisos."
            ),
            inline=False
        )

        embed.set_footer(
            text="The Warriors • Utilidades"
        )

        await ctx.send(
            embed=embed,
            ephemeral=True
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    if bot.get_cog("Utilidades") is not None:

        print(
            "⚠️ Utilidades ya estaba cargado."
        )

        return

    await bot.add_cog(
        Utilidades(bot)
    )

    print(
        "✅ Utilidades.py cargado correctamente."
    )
