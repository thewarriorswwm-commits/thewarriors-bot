import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from zoneinfo import ZoneInfo


# ============================================================
# CONFIGURACIÓN
# ============================================================

CANAL_GUERRAS = "guerras-⚔️"
CANAL_REGISTRO = "registro-guerra"

ZONA_HORARIA = ZoneInfo("Europe/Madrid")

ROLES_GUERRA = [
    "DPS",
    "DPS Distancia",
    "Healer",
    "Tank",
    "No asistiré"
]


# ============================================================
# CREAR / OBTENER ROLES
# ============================================================

async def asegurar_roles(guild):

    roles = {}

    roles_servidor = {
        rol.name: rol
        for rol in guild.roles
    }

    for nombre in ROLES_GUERRA:

        rol = roles_servidor.get(nombre)

        if rol is None:

            try:

                rol = await guild.create_role(
                    name=nombre,
                    reason="Sistema de inscripción de guerras"
                )

                print(
                    f"✅ Rol creado: {nombre}"
                )

            except discord.Forbidden:

                print(
                    f"❌ No puedo crear el rol: {nombre}"
                )

                continue

            except discord.HTTPException as error:

                print(
                    f"❌ Error creando {nombre}: {error}"
                )

                continue

        roles[nombre] = rol

    return roles


# ============================================================
# BUSCAR REGISTRO
# ============================================================

async def buscar_registro(
    canal,
    usuario_id,
    dia
):

    try:

        async for mensaje in canal.history(
            limit=100
        ):

            if mensaje.author.id != canal.guild.me.id:
                continue

            if not mensaje.embeds:
                continue

            embed = mensaje.embeds[0]

            if embed.title != "⚔️ Registro de guerra":
                continue

            usuario_encontrado = False
            dia_encontrado = False

            for campo in embed.fields:

                if campo.name == "🆔 Usuario":

                    if campo.value == str(usuario_id):

                        usuario_encontrado = True

                elif campo.name == "📅 Día":

                    if campo.value.lower() == dia.lower():

                        dia_encontrado = True

            if usuario_encontrado and dia_encontrado:

                return mensaje

    except discord.Forbidden:

        print(
            "❌ No puedo leer #registro-guerra."
        )

    except discord.HTTPException as error:

        print(
            f"❌ Error leyendo #registro-guerra: {error}"
        )

    return None


# ============================================================
# GUARDAR / ACTUALIZAR REGISTRO
# ============================================================

async def guardar_registro(
    guild,
    usuario,
    rol,
    dia
):

    canal = discord.utils.get(
        guild.text_channels,
        name=CANAL_REGISTRO
    )

    if canal is None:

        print(
            "❌ No existe #registro-guerra"
        )

        return

    registro_existente = await buscar_registro(
        canal,
        usuario.id,
        dia
    )

    embed = discord.Embed(
        title="⚔️ Registro de guerra",
        color=discord.Color.green()
    )

    embed.add_field(
        name="👤 Nombre",
        value=usuario.mention,
        inline=False
    )

    embed.add_field(
        name="🆔 Usuario",
        value=str(usuario.id),
        inline=False
    )

    embed.add_field(
        name="🎭 Rol",
        value=rol.mention,
        inline=False
    )

    embed.add_field(
        name="📅 Día",
        value=dia.capitalize(),
        inline=False
    )

    # ========================================================
    # ACTUALIZAR
    # ========================================================

    if registro_existente is not None:

        try:

            await registro_existente.edit(
                embed=embed
            )

            print(
                f"🔄 Registro actualizado: "
                f"{usuario} — {dia}"
            )

            return

        except discord.Forbidden:

            print(
                "❌ No puedo editar el registro."
            )

            return

        except discord.HTTPException as error:

            print(
                f"❌ Error actualizando registro: {error}"
            )

            return

    # ========================================================
    # CREAR
    # ========================================================

    try:

        await canal.send(
            embed=embed
        )

        print(
            f"📝 Registro creado: "
            f"{usuario} — {dia}"
        )

    except discord.Forbidden:

        print(
            "❌ No puedo escribir en #registro-guerra."
        )

    except discord.HTTPException as error:

        print(
            f"❌ Error creando registro: {error}"
        )


# ============================================================
# PANEL DE GUERRA
# ============================================================

class GuerraView(discord.ui.View):

    def __init__(
        self,
        dia
    ):

        super().__init__(
            timeout=None
        )

        self.dia = dia

    # ========================================================
    # ELEGIR ROL
    # ========================================================

    async def elegir_rol(
        self,
        interaction,
        nombre_rol
    ):

        guild = interaction.guild

        if guild is None:

            await interaction.response.send_message(
                "❌ Este botón solo funciona dentro de un servidor.",
                ephemeral=True
            )

            return

        try:

            roles = await asegurar_roles(
                guild
            )

            rol_elegido = roles.get(
                nombre_rol
            )

            if rol_elegido is None:

                await interaction.response.send_message(
                    "❌ No puedo encontrar o crear "
                    "el rol de guerra.",
                    ephemeral=True
                )

                return

            # =================================================
            # QUITAR OTROS ROLES DE GUERRA
            # =================================================

            roles_a_quitar = [
                rol
                for nombre, rol in roles.items()
                if rol != rol_elegido
                and rol in interaction.user.roles
            ]

            if roles_a_quitar:

                await interaction.user.remove_roles(
                    *roles_a_quitar,
                    reason="Cambio de rol de guerra"
                )

            # =================================================
            # DAR ROL
            # =================================================

            if rol_elegido not in interaction.user.roles:

                await interaction.user.add_roles(
                    rol_elegido,
                    reason=f"Inscripción guerra {self.dia}"
                )

            # =================================================
            # GUARDAR REGISTRO
            # =================================================

            await guardar_registro(
                guild,
                interaction.user,
                rol_elegido,
                self.dia
            )

            # =================================================
            # RESPUESTA
            # =================================================

            await interaction.response.send_message(
                f"✅ **Inscripción realizada.**\n\n"
                f"⚔️ Guerra: **{self.dia.capitalize()}**\n"
                f"🎭 Rol: **{nombre_rol}**\n\n"
                "Tu elección solo la puedes ver tú.",
                ephemeral=True
            )

        except discord.Forbidden:

            if not interaction.response.is_done():

                await interaction.response.send_message(
                    "❌ No puedo modificar tus roles.\n\n"
                    "Comprueba que el rol del bot esté "
                    "por encima de los roles de guerra.",
                    ephemeral=True
                )

        except discord.HTTPException as error:

            print(
                f"❌ Error de Discord: {error}"
            )

            if not interaction.response.is_done():

                await interaction.response.send_message(
                    "❌ Discord no ha permitido realizar "
                    "la inscripción.",
                    ephemeral=True
                )

        except Exception as error:

            print(
                f"❌ Error en guerra: {error}"
            )

            if not interaction.response.is_done():

                await interaction.response.send_message(
                    "❌ Ha ocurrido un error al registrarte.",
                    ephemeral=True
                )

    # ========================================================
    # DPS
    # ========================================================

    @discord.ui.button(
        label="DPS",
        emoji="⚔️",
        style=discord.ButtonStyle.danger,
        custom_id="guerra_dps"
    )
    async def dps(
        self,
        interaction,
        button
    ):

        await self.elegir_rol(
            interaction,
            "DPS"
        )

    # ========================================================
    # DPS DISTANCIA
    # ========================================================

    @discord.ui.button(
        label="DPS Distancia",
        emoji="🏹",
        style=discord.ButtonStyle.primary,
        custom_id="guerra_dps_distancia"
    )
    async def dps_distancia(
        self,
        interaction,
        button
    ):

        await self.elegir_rol(
            interaction,
            "DPS Distancia"
        )

    # ========================================================
    # HEALER
    # ========================================================

    @discord.ui.button(
        label="Healer",
        emoji="💚",
        style=discord.ButtonStyle.success,
        custom_id="guerra_healer"
    )
    async def healer(
        self,
        interaction,
        button
    ):

        await self.elegir_rol(
            interaction,
            "Healer"
        )

    # ========================================================
    # TANK
    # ========================================================

    @discord.ui.button(
        label="Tank",
        emoji="🛡️",
        style=discord.ButtonStyle.secondary,
        custom_id="guerra_tank"
    )
    async def tank(
        self,
        interaction,
        button
    ):

        await self.elegir_rol(
            interaction,
            "Tank"
        )

    # ========================================================
    # NO ASISTIRÉ
    # ========================================================

    @discord.ui.button(
        label="No asistiré",
        emoji="❌",
        style=discord.ButtonStyle.secondary,
        custom_id="guerra_no_asistire"
    )
    async def no_asistire(
        self,
        interaction,
        button
    ):

        await self.elegir_rol(
            interaction,
            "No asistiré"
        )


# ============================================================
# PUBLICAR PANELES
# ============================================================

async def publicar_paneles(
    guild
):

    canal = discord.utils.get(
        guild.text_channels,
        name=CANAL_GUERRAS
    )

    if canal is None:

        print(
            f"❌ No encuentro #{CANAL_GUERRAS}"
        )

        return

    await asegurar_roles(
        guild
    )

    # ========================================================
    # AVISO
    # ========================================================

    await canal.send(
        "🔔 **INSCRIPCIONES ABIERTAS**\n\n"
        "Ya puedes apuntarte a las guerras "
        "del **sábado y domingo**.\n\n"
        "Selecciona tu rol en el panel correspondiente."
    )

    # ========================================================
    # SÁBADO
    # ========================================================

    embed_sabado = discord.Embed(
        title="⚔️ GUERRA — SÁBADO",
        description=(
            "### 📋 INSCRIPCIÓN\n\n"
            "Selecciona tu rol:\n\n"
            "⚔️ **DPS**\n"
            "🏹 **DPS Distancia**\n"
            "💚 **Healer**\n"
            "🛡️ **Tank**\n"
            "❌ **No asistiré**\n\n"
            "🕢 **19:30**\n"
            "Preferiblemente estar en llamada "
            "para organizar el sistema.\n\n"
            "🕣 **20:30**\n"
            "Comienza la guerra."
        ),
        color=discord.Color.blue()
    )

    embed_sabado.set_footer(
        text="Guerra del sábado"
    )

    await canal.send(
        embed=embed_sabado,
        view=GuerraView(
            "sábado"
        )
    )

    # ========================================================
    # DOMINGO
    # ========================================================

    embed_domingo = discord.Embed(
        title="⚔️ GUERRA — DOMINGO",
        description=(
            "### 📋 INSCRIPCIÓN\n\n"
            "Selecciona tu rol:\n\n"
            "⚔️ **DPS**\n"
            "🏹 **DPS Distancia**\n"
            "💚 **Healer**\n"
            "🛡️ **Tank**\n"
            "❌ **No asistiré**\n\n"
            "🕢 **19:30**\n"
            "Preferiblemente estar en llamada "
            "para organizar el sistema.\n\n"
            "🕣 **20:30**\n"
            "Comienza la guerra."
        ),
        color=discord.Color.purple()
    )

    embed_domingo.set_footer(
        text="Guerra del domingo"
    )

    await canal.send(
        embed=embed_domingo,
        view=GuerraView(
            "domingo"
        )
    )

    print(
        f"✅ Paneles de guerra publicados "
        f"en {guild.name}"
    )


# ============================================================
# COG GUERRAS
# ============================================================

class Guerras(
    commands.Cog
):

    def __init__(
        self,
        bot
    ):

        self.bot = bot

        self.scheduler = AsyncIOScheduler(
            timezone=ZONA_HORARIA
        )

        print(
            "🟢 Guerras.py cargado"
        )

    # ========================================================
    # COMANDO PANEL DE GUERRA
    # ========================================================

    @commands.command(
        name="panelguerra"
    )
    @commands.has_permissions(
        administrator=True
    )
    async def panel_guerra(
        self,
        ctx
    ):

        if ctx.channel.name != CANAL_GUERRAS:

            await ctx.send(
                f"❌ Este comando solo funciona "
                f"en #{CANAL_GUERRAS}.",
                delete_after=5
            )

            return

        await publicar_paneles(
            ctx.guild
        )

        await ctx.send(
            "✅ **Paneles de guerra publicados.**",
            delete_after=5
        )

    # ========================================================
    # AUTOMÁTICO — MIÉRCOLES 17:00
    # ========================================================

    async def aviso_automatico(
        self
    ):

        for guild in self.bot.guilds:

            try:

                await publicar_paneles(
                    guild
                )

            except Exception as error:

                print(
                    f"❌ Error en {guild.name}: {error}"
                )

    # ========================================================
    # LIMPIAR REGISTRO + PANELES — LUNES 00:00
    # ========================================================

    async def limpiar_registro(
        self
    ):

        for guild in self.bot.guilds:

            # =================================================
            # BORRAR REGISTRO
            # =================================================

            canal = discord.utils.get(
                guild.text_channels,
                name=CANAL_REGISTRO
            )

            if canal is not None:

                try:

                    async for mensaje in canal.history(
                        limit=None
                    ):

                        if mensaje.author.id == self.bot.user.id:

                            try:

                                await mensaje.delete()

                            except discord.NotFound:

                                pass

                            except discord.HTTPException as error:

                                print(
                                    f"❌ Error borrando registro: "
                                    f"{error}"
                                )

                    print(
                        f"🧹 Registro limpiado en "
                        f"{guild.name}"
                    )

                except discord.Forbidden:

                    print(
                        "❌ No tengo permisos para "
                        "limpiar #registro-guerra."
                    )

                except discord.HTTPException as error:

                    print(
                        f"❌ Error limpiando registro: "
                        f"{error}"
                    )

            # =================================================
            # BORRAR PANELES
            # =================================================

            canal_guerras = discord.utils.get(
                guild.text_channels,
                name=CANAL_GUERRAS
            )

            if canal_guerras is not None:

                try:

                    async for mensaje in canal_guerras.history(
                        limit=None
                    ):

                        if mensaje.author.id == self.bot.user.id:

                            try:

                                await mensaje.delete()

                            except discord.NotFound:

                                pass

                            except discord.HTTPException as error:

                                print(
                                    f"❌ Error borrando panel: "
                                    f"{error}"
                                )

                    print(
                        f"🧹 Paneles de guerra limpiados "
                        f"en {guild.name}"
                    )

                except discord.Forbidden:

                    print(
                        "❌ No tengo permisos para "
                        "limpiar #guerras-⚔️."
                    )

                except discord.HTTPException as error:

                    print(
                        f"❌ Error limpiando paneles: "
                        f"{error}"
                    )

    # ========================================================
    # BOT READY
    # ========================================================

    @commands.Cog.listener()
    async def on_ready(
        self
    ):

        if self.scheduler.running:

            return

        # ====================================================
        # MIÉRCOLES 17:00
        # ====================================================

        self.scheduler.add_job(
            self.aviso_automatico,
            "cron",
            day_of_week="wed",
            hour=17,
            minute=0,
            id="aviso_guerras",
            replace_existing=True
        )

        # ====================================================
        # LUNES 00:00
        # ====================================================

        self.scheduler.add_job(
            self.limpiar_registro,
            "cron",
            day_of_week="mon",
            hour=0,
            minute=0,
            id="limpiar_registro",
            replace_existing=True
        )

        self.scheduler.start()

        print(
            "⚔️ Sistema automático de guerras iniciado."
        )


# ============================================================
# SETUP
# ============================================================

async def setup(
    bot
):

    bot.add_view(
        GuerraView(
            "sábado"
        )
    )

    bot.add_view(
        GuerraView(
            "domingo"
        )
    )

    await bot.add_cog(
        Guerras(bot)
    )

    print(
        "✅ Guerras.py instalado correctamente."
    )

