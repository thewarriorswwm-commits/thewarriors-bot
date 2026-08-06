import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta


# ============================================================
# CONFIGURACIÓN
# ============================================================

CANAL_GUERRAS = "guerras-⚔️"
CANAL_REGISTRO = "registro-guerra-📋"

ZONA_HORARIA = ZoneInfo("Europe/Madrid")

ROLES_GUERRA = [
    "DPS",
    "DPS Distancia",
    "Healer",
    "Tank",
    "No asistiré"
]


# ============================================================
# FECHAS
# ============================================================

def obtener_fecha_guerra(dia):

    ahora = datetime.now(ZONA_HORARIA)
    fecha_actual = ahora.date()

    dias_semana = {
        "lunes": 0,
        "martes": 1,
        "miércoles": 2,
        "jueves": 3,
        "viernes": 4,
        "sábado": 5,
        "domingo": 6
    }

    objetivo = dias_semana[dia.lower()]

    diferencia = (
        objetivo - fecha_actual.weekday()
    ) % 7

    return fecha_actual + timedelta(days=diferencia)


def formatear_fecha(fecha):
    return fecha.strftime("%d/%m/%Y")


# ============================================================
# CREAR / OBTENER ROLES
# ============================================================

async def asegurar_roles(guild):

    roles = {}

    for nombre in ROLES_GUERRA:

        rol = discord.utils.get(
            guild.roles,
            name=nombre
        )

        if rol is None:

            try:

                rol = await guild.create_role(
                    name=nombre,
                    reason="Sistema de inscripción de guerras"
                )

                print(f"✅ Rol creado: {nombre}")

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
# BUSCAR REGISTRO EXISTENTE
# ============================================================

async def buscar_registro(
    canal,
    usuario_id,
    fecha
):

    fecha_texto = formatear_fecha(fecha)

    try:

        async for mensaje in canal.history(
            limit=None
        ):

            if mensaje.author != canal.guild.me:
                continue

            if not mensaje.embeds:
                continue

            embed = mensaje.embeds[0]

            if embed.title != "⚔️ Registro de guerra":
                continue

            usuario_encontrado = False
            fecha_encontrada = False

            for campo in embed.fields:

                if campo.name == "🆔 Usuario":

                    if campo.value == str(usuario_id):
                        usuario_encontrado = True

                elif campo.name == "📅 Fecha":

                    if campo.value == fecha_texto:
                        fecha_encontrada = True

            if usuario_encontrado and fecha_encontrada:

                return mensaje

    except discord.Forbidden:

        print(
            f"⚠️ No puedo leer el historial de #{canal.name}"
        )

    except discord.HTTPException as error:

        print(
            f"⚠️ Error leyendo registros: {error}"
        )

    return None


# ============================================================
# BUSCAR CANAL DE REGISTRO
# ============================================================

def buscar_canal_registro(guild):

    # Primero busca el nombre exacto

    canal = discord.utils.get(
        guild.text_channels,
        name=CANAL_REGISTRO
    )

    if canal is not None:
        return canal

    # Si no coincide exactamente,
    # busca cualquier canal que empiece por registro-guerra

    for canal in guild.text_channels:

        if canal.name.startswith("registro-guerra"):

            return canal

    return None


# ============================================================
# GUARDAR / ACTUALIZAR REGISTRO
# ============================================================

async def guardar_registro(
    guild,
    usuario,
    rol,
    dia,
    fecha
):

    fecha_texto = formatear_fecha(fecha)

    # ========================================================
    # BUSCAR CANAL
    # ========================================================

    canal = buscar_canal_registro(guild)

    # ========================================================
    # CREAR CANAL SI NO EXISTE
    # ========================================================

    if canal is None:

        print(
            f"⚠️ No encuentro #{CANAL_REGISTRO}"
        )

        try:

            canal = await guild.create_text_channel(
                CANAL_REGISTRO,
                reason="Crear canal para registros de guerras"
            )

            print(
                f"✅ Canal creado: #{canal.name}"
            )

        except discord.Forbidden:

            print(
                "❌ No tengo permiso para crear "
                "el canal de registro."
            )

            return False

        except discord.HTTPException as error:

            print(
                f"❌ Error creando canal: {error}"
            )

            return False

    # ========================================================
    # COMPROBAR CANAL
    # ========================================================

    print(
        f"📋 Canal de registro: #{canal.name}"
    )

    # ========================================================
    # COMPROBAR BOT
    # ========================================================

    bot_member = guild.me

    if bot_member is None:

        print(
            "❌ No encuentro al bot dentro del servidor."
        )

        return False

    # ========================================================
    # COMPROBAR PERMISOS
    # ========================================================

    permisos = canal.permissions_for(bot_member)

    if not permisos.view_channel:

        print(
            f"❌ El bot NO PUEDE VER #{canal.name}"
        )

        return False

    if not permisos.send_messages:

        print(
            f"❌ El bot NO PUEDE ESCRIBIR "
            f"en #{canal.name}"
        )

        return False

    if not permisos.read_message_history:

        print(
            f"⚠️ El bot NO PUEDE LEER HISTORIAL "
            f"de #{canal.name}"
        )

        # No detenemos el envío.
        # Solo impedirá encontrar un registro anterior.

    # ========================================================
    # BUSCAR REGISTRO EXISTENTE
    # ========================================================

    registro_existente = None

    if permisos.read_message_history:

        registro_existente = await buscar_registro(
            canal,
            usuario.id,
            fecha
        )

    # ========================================================
    # CREAR EMBED
    # ========================================================

    embed = discord.Embed(
        title="⚔️ Registro de guerra",
        description=(
            f"**{usuario.display_name}** "
            "se ha inscrito en la guerra."
        ),
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
        name="📆 Día",
        value=dia.capitalize(),
        inline=False
    )

    embed.add_field(
        name="📅 Fecha",
        value=fecha_texto,
        inline=False
    )

    # ========================================================
    # ACTUALIZAR REGISTRO
    # ========================================================

    if registro_existente is not None:

        try:

            await registro_existente.edit(
                embed=embed
            )

            print(
                "✅ REGISTRO ACTUALIZADO"
            )

            return True

        except discord.Forbidden:

            print(
                "⚠️ No puedo editar el registro."
            )

        except discord.HTTPException as error:

            print(
                f"⚠️ Error editando registro: {error}"
            )

    # ========================================================
    # ENVIAR NUEVO REGISTRO
    # ========================================================

    try:

        mensaje = await canal.send(
            embed=embed
        )

        print(
            "=========================================="
        )

        print(
            "✅ REGISTRO ENVIADO CORRECTAMENTE"
        )

        print(
            f"👤 Usuario: {usuario}"
        )

        print(
            f"🎭 Rol: {rol.name}"
        )

        print(
            f"⚔️ Día: {dia}"
        )

        print(
            f"📅 Fecha: {fecha_texto}"
        )

        print(
            f"📋 Canal: #{canal.name}"
        )

        print(
            f"🆔 Mensaje ID: {mensaje.id}"
        )

        print(
            "=========================================="
        )

        return True

    except discord.Forbidden as error:

        print(
            "=========================================="
        )

        print(
            "❌ DISCORD NO DEJA ENVIAR EL REGISTRO"
        )

        print(
            f"📋 Canal: #{canal.name}"
        )

        print(
            f"❌ Error: {error}"
        )

        print(
            "Necesitas que el bot tenga:"
        )

        print(
            "✅ Ver canal"
        )

        print(
            "✅ Enviar mensajes"
        )

        print(
            "=========================================="
        )

        return False

    except discord.HTTPException as error:

        print(
            "=========================================="
        )

        print(
            f"❌ ERROR DE DISCORD: {error}"
        )

        print(
            "=========================================="
        )

        return False

    except Exception as error:

        print(
            "=========================================="
        )

        print(
            f"❌ ERROR REGISTRANDO: {error}"
        )

        print(
            "=========================================="
        )

        return False


# ============================================================
# ELEGIR ROL
# ============================================================

async def procesar_inscripcion(
    interaction,
    nombre_rol,
    dia,
    fecha
):

    guild = interaction.guild

    if guild is None:

        await interaction.response.send_message(
            "❌ Este botón solo funciona dentro de un servidor.",
            ephemeral=True
        )

        return

    try:

        # ====================================================
        # ASEGURAR ROLES
        # ====================================================

        roles = await asegurar_roles(guild)

        rol_elegido = roles.get(nombre_rol)

        if rol_elegido is None:

            await interaction.response.send_message(
                "❌ No puedo encontrar o crear "
                "el rol de guerra.",
                ephemeral=True
            )

            return

        # ====================================================
        # QUITAR OTROS ROLES DE GUERRA
        # ====================================================

        for rol in roles.values():

            if rol == rol_elegido:
                continue

            if rol in interaction.user.roles:

                await interaction.user.remove_roles(
                    rol,
                    reason="Cambio de rol de guerra"
                )

        # ====================================================
        # DAR ROL ELEGIDO
        # ====================================================

        if rol_elegido not in interaction.user.roles:

            await interaction.user.add_roles(
                rol_elegido,
                reason=(
                    f"Inscripción guerra "
                    f"{dia} "
                    f"{formatear_fecha(fecha)}"
                )
            )

        # ====================================================
        # GUARDAR REGISTRO
        # ====================================================

        registro_guardado = await guardar_registro(
            guild,
            interaction.user,
            rol_elegido,
            dia,
            fecha
        )

        # ====================================================
        # REGISTRO NO GUARDADO
        # ====================================================

        if not registro_guardado:

            await interaction.response.send_message(
                "⚠️ **Te has inscrito correctamente**, "
                "pero el registro no pudo guardarse.\n\n"
                f"📋 Canal: #{CANAL_REGISTRO}\n\n"
                "El administrador debe revisar los "
                "permisos del bot en ese canal.",
                ephemeral=True
            )

            return

        # ====================================================
        # RESPUESTA CORRECTA
        # ====================================================

        await interaction.response.send_message(
            f"✅ **Inscripción realizada.**\n\n"
            f"⚔️ Guerra: **{dia.capitalize()}**\n"
            f"📅 Fecha: **{formatear_fecha(fecha)}**\n"
            f"🎭 Rol: **{nombre_rol}**\n\n"
            "Tu elección solo la puedes ver tú.",
            ephemeral=True
        )

    except discord.Forbidden:

        print(
            "❌ Discord ha rechazado una operación "
            "por falta de permisos."
        )

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


# ============================================================
# VISTA SÁBADO
# ============================================================

class GuerraSabadoView(discord.ui.View):

    def __init__(self, fecha):

        super().__init__(
            timeout=None
        )

        self.fecha = fecha

    @discord.ui.button(
        label="DPS",
        emoji="⚔️",
        style=discord.ButtonStyle.danger,
        custom_id="guerra_sabado_dps"
    )
    async def dps(
        self,
        interaction,
        button
    ):

        await procesar_inscripcion(
            interaction,
            "DPS",
            "sábado",
            self.fecha
        )

    @discord.ui.button(
        label="DPS Distancia",
        emoji="🏹",
        style=discord.ButtonStyle.primary,
        custom_id="guerra_sabado_dps_distancia"
    )
    async def dps_distancia(
        self,
        interaction,
        button
    ):

        await procesar_inscripcion(
            interaction,
            "DPS Distancia",
            "sábado",
            self.fecha
        )

    @discord.ui.button(
        label="Healer",
        emoji="💚",
        style=discord.ButtonStyle.success,
        custom_id="guerra_sabado_healer"
    )
    async def healer(
        self,
        interaction,
        button
    ):

        await procesar_inscripcion(
            interaction,
            "Healer",
            "sábado",
            self.fecha
        )

    @discord.ui.button(
        label="Tank",
        emoji="🛡️",
        style=discord.ButtonStyle.secondary,
        custom_id="guerra_sabado_tank"
    )
    async def tank(
        self,
        interaction,
        button
    ):

        await procesar_inscripcion(
            interaction,
            "Tank",
            "sábado",
            self.fecha
        )

    @discord.ui.button(
        label="No asistiré",
        emoji="❌",
        style=discord.ButtonStyle.secondary,
        custom_id="guerra_sabado_no_asistire"
    )
    async def no_asistire(
        self,
        interaction,
        button
    ):

        await procesar_inscripcion(
            interaction,
            "No asistiré",
            "sábado",
            self.fecha
        )


# ============================================================
# VISTA DOMINGO
# ============================================================

class GuerraDomingoView(discord.ui.View):

    def __init__(self, fecha):

        super().__init__(
            timeout=None
        )

        self.fecha = fecha

    @discord.ui.button(
        label="DPS",
        emoji="⚔️",
        style=discord.ButtonStyle.danger,
        custom_id="guerra_domingo_dps"
    )
    async def dps(
        self,
        interaction,
        button
    ):

        await procesar_inscripcion(
            interaction,
            "DPS",
            "domingo",
            self.fecha
        )

    @discord.ui.button(
        label="DPS Distancia",
        emoji="🏹",
        style=discord.ButtonStyle.primary,
        custom_id="guerra_domingo_dps_distancia"
    )
    async def dps_distancia(
        self,
        interaction,
        button
    ):

        await procesar_inscripcion(
            interaction,
            "DPS Distancia",
            "domingo",
            self.fecha
        )

    @discord.ui.button(
        label="Healer",
        emoji="💚",
        style=discord.ButtonStyle.success,
        custom_id="guerra_domingo_healer"
    )
    async def healer(
        self,
        interaction,
        button
    ):

        await procesar_inscripcion(
            interaction,
            "Healer",
            "domingo",
            self.fecha
        )

    @discord.ui.button(
        label="Tank",
        emoji="🛡️",
        style=discord.ButtonStyle.secondary,
        custom_id="guerra_domingo_tank"
    )
    async def tank(
        self,
        interaction,
        button
    ):

        await procesar_inscripcion(
            interaction,
            "Tank",
            "domingo",
            self.fecha
        )

    @discord.ui.button(
        label="No asistiré",
        emoji="❌",
        style=discord.ButtonStyle.secondary,
        custom_id="guerra_domingo_no_asistire"
    )
    async def no_asistire(
        self,
        interaction,
        button
    ):

        await procesar_inscripcion(
            interaction,
            "No asistiré",
            "domingo",
            self.fecha
        )


# ============================================================
# PUBLICAR PANELES
# ============================================================

async def publicar_paneles(guild):

    canal = discord.utils.get(
        guild.text_channels,
        name=CANAL_GUERRAS
    )

    if canal is None:

        print(
            f"❌ No encuentro #{CANAL_GUERRAS}"
        )

        return

    fecha_sabado = obtener_fecha_guerra(
        "sábado"
    )

    fecha_domingo = obtener_fecha_guerra(
        "domingo"
    )

    await asegurar_roles(guild)

    # ========================================================
    # AVISO
    # ========================================================

    await canal.send(
        "🔔 **INSCRIPCIONES ABIERTAS**\n\n"
        f"⚔️ **Sábado — {formatear_fecha(fecha_sabado)}**\n"
        f"⚔️ **Domingo — {formatear_fecha(fecha_domingo)}**\n\n"
        "Ya puedes apuntarte a las próximas guerras.\n\n"
        "Selecciona tu rol en el panel correspondiente."
    )

    # ========================================================
    # PANEL SÁBADO
    # ========================================================

    embed_sabado = discord.Embed(
        title="⚔️ GUERRA — SÁBADO",
        description=(
            "### 📋 INSCRIPCIÓN\n\n"
            f"📅 **Fecha: {formatear_fecha(fecha_sabado)}**\n\n"
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
        view=GuerraSabadoView(
            fecha_sabado
        )
    )

    # ========================================================
    # PANEL DOMINGO
    # ========================================================

    embed_domingo = discord.Embed(
        title="⚔️ GUERRA — DOMINGO",
        description=(
            "### 📋 INSCRIPCIÓN\n\n"
            f"📅 **Fecha: {formatear_fecha(fecha_domingo)}**\n\n"
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
        view=GuerraDomingoView(
            fecha_domingo
        )
    )

    print(
        f"✅ Paneles de guerra publicados en {guild.name}"
    )


# ============================================================
# LIMPIAR ROLES DE GUERRA
# ============================================================

async def limpiar_roles_guerra(guild):

    roles = await asegurar_roles(guild)

    for miembro in guild.members:

        roles_a_quitar = [
            rol
            for rol in roles.values()
            if rol in miembro.roles
        ]

        if not roles_a_quitar:
            continue

        try:

            await miembro.remove_roles(
                *roles_a_quitar,
                reason="Limpieza semanal de roles de guerra"
            )

            print(
                f"🧹 Roles de guerra eliminados de {miembro}"
            )

        except discord.Forbidden:

            print(
                f"❌ No puedo quitar roles de {miembro}"
            )

        except discord.HTTPException as error:

            print(
                f"❌ Error quitando roles de {miembro}: {error}"
            )


# ============================================================
# BORRAR MENSAJES DEL BOT
# ============================================================

async def borrar_mensajes_del_bot(canal):

    try:

        async for mensaje in canal.history(
            limit=None
        ):

            if mensaje.author != canal.guild.me:
                continue

            try:

                await mensaje.delete()

            except discord.NotFound:

                pass

        return True

    except discord.Forbidden:

        print(
            f"❌ No tengo permiso para borrar mensajes "
            f"en #{canal.name}"
        )

    except discord.HTTPException as error:

        print(
            f"❌ Error borrando mensajes en "
            f"#{canal.name}: {error}"
        )

    return False


# ============================================================
# COG GUERRAS
# ============================================================

class Guerras(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        self.scheduler = AsyncIOScheduler(
            timezone=ZONA_HORARIA
        )

        print(
            "🟢 Guerras.py cargado"
        )

    # ========================================================
    # COMANDO MANUAL
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

        if ctx.guild is None:
            return

        if ctx.channel.name != CANAL_GUERRAS:

            await ctx.send(
                f"❌ Este comando solo funciona "
                f"en #{CANAL_GUERRAS}.",
                delete_after=5
            )

            return

        try:

            await publicar_paneles(
                ctx.guild
            )

            await ctx.send(
                "✅ **Paneles de guerra lanzados manualmente.**",
                delete_after=5
            )

        except Exception as error:

            print(
                f"❌ Error lanzando panel manual: {error}"
            )

            await ctx.send(
                "❌ No se pudieron lanzar "
                "los paneles de guerra.",
                delete_after=5
            )

    # ========================================================
    # AUTOMÁTICO — MIÉRCOLES 17:00
    # ========================================================

    async def aviso_automatico(self):

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
    # LIMPIAR TODO — LUNES 00:00
    # ========================================================

    async def limpiar_registro(self):

        for guild in self.bot.guilds:

            # =================================================
            # BORRAR REGISTROS
            # =================================================

            canal_registro = buscar_canal_registro(
                guild
            )

            if canal_registro is not None:

                resultado = await borrar_mensajes_del_bot(
                    canal_registro
                )

                if resultado:

                    print(
                        f"🧹 Registro limpiado en {guild.name}"
                    )

            else:

                print(
                    f"⚠️ No existe #{CANAL_REGISTRO}"
                )

            # =================================================
            # BORRAR PANELES
            # =================================================

            canal_guerras = discord.utils.get(
                guild.text_channels,
                name=CANAL_GUERRAS
            )

            if canal_guerras is not None:

                resultado = await borrar_mensajes_del_bot(
                    canal_guerras
                )

                if resultado:

                    print(
                        f"🗑️ Paneles de guerra borrados "
                        f"en {guild.name}"
                    )

            else:

                print(
                    f"⚠️ No existe #{CANAL_GUERRAS}"
                )

            # =================================================
            # QUITAR ROLES
            # =================================================

            try:

                await limpiar_roles_guerra(
                    guild
                )

                print(
                    f"🎭 Roles de guerra limpiados "
                    f"en {guild.name}"
                )

            except Exception as error:

                print(
                    f"❌ Error limpiando roles en "
                    f"{guild.name}: {error}"
                )

    # ========================================================
    # BOT READY
    # ========================================================

    @commands.Cog.listener()
    async def on_ready(self):

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

async def setup(bot):

    await bot.add_cog(
        Guerras(bot)
    )

    # ========================================================
    # VISTAS PERSISTENTES
    # ========================================================

    bot.add_view(
        GuerraSabadoView(
            obtener_fecha_guerra("sábado")
        )
    )

    bot.add_view(
        GuerraDomingoView(
            obtener_fecha_guerra("domingo")
        )
    )

    print(
        "✅ Guerras.py instalado correctamente."
    )
