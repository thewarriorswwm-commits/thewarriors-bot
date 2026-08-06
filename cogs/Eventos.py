import discord
from discord.ext import commands
from pathlib import Path
import json
import asyncio


# ============================================================
# CONFIGURACIÓN
# ============================================================

CANAL_EVENTOS = "eventos-📅"

ARCHIVO_EVENTOS = Path("data/eventos.json")


# ============================================================
# BASE DE DATOS
# ============================================================

def cargar_eventos():

    ARCHIVO_EVENTOS.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if not ARCHIVO_EVENTOS.exists():

        ARCHIVO_EVENTOS.write_text(
            "{}",
            encoding="utf-8"
        )

        return {}

    try:

        contenido = ARCHIVO_EVENTOS.read_text(
            encoding="utf-8"
        )

        datos = json.loads(contenido)

        if isinstance(datos, dict):
            return datos

    except Exception as error:

        print(
            f"❌ Error leyendo eventos.json: {error}"
        )

    return {}


EVENTOS = cargar_eventos()

LOCK_EVENTOS = asyncio.Lock()


# ============================================================
# GUARDAR EVENTOS
# ============================================================

async def guardar_eventos():

    async with LOCK_EVENTOS:

        try:

            ARCHIVO_EVENTOS.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            ARCHIVO_EVENTOS.write_text(
                json.dumps(
                    EVENTOS,
                    ensure_ascii=False,
                    indent=4
                ),
                encoding="utf-8"
            )

        except Exception as error:

            print(
                f"❌ Error guardando eventos: {error}"
            )


# ============================================================
# CREAR EMBED DEL EVENTO
# ============================================================

def crear_embed_evento(evento):

    inscritos = evento.get(
        "inscritos",
        []
    )

    if inscritos:

        lista = "\n".join(
            f"• <@{usuario_id}>"
            for usuario_id in inscritos
        )

    else:

        lista = "Nadie se ha inscrito todavía."

    embed = discord.Embed(
        title="🎉 EVENTO",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="🎯 Tipo de evento",
        value=evento["tipo"],
        inline=False
    )

    embed.add_field(
        name="📅 Fecha",
        value=evento["fecha"],
        inline=True
    )

    embed.add_field(
        name="🕐 Hora",
        value=evento["hora"],
        inline=True
    )

    embed.add_field(
        name=f"👥 INSCRITOS ({len(inscritos)})",
        value=lista,
        inline=False
    )

    embed.set_footer(
        text="Usa los botones para inscribirte o cancelar."
    )

    return embed


# ============================================================
# ACTUALIZAR MENSAJE DEL EVENTO
# ============================================================

async def actualizar_evento(
    canal,
    mensaje_id,
    evento
):

    try:

        mensaje = await canal.fetch_message(
            int(mensaje_id)
        )

        await mensaje.edit(
            embed=crear_embed_evento(evento),
            view=EventoView(mensaje_id)
        )

        return True

    except discord.NotFound:

        print(
            f"❌ No encuentro el mensaje del evento {mensaje_id}."
        )

    except discord.Forbidden:

        print(
            "❌ No tengo permisos para editar el evento."
        )

    except discord.HTTPException as error:

        print(
            f"❌ Error actualizando evento: {error}"
        )

    return False


# ============================================================
# MODAL CREAR EVENTO
# ============================================================

class CrearEventoModal(
    discord.ui.Modal,
    title="🛠️ Crear evento"
):

    tipo = discord.ui.TextInput(
        label="🎯 Tipo de evento",
        placeholder="Ejemplo: Raid, PvP, Mazmorra...",
        required=True,
        max_length=100
    )

    fecha = discord.ui.TextInput(
        label="📅 Fecha",
        placeholder="Ejemplo: 15/08/2026",
        required=True,
        max_length=20
    )

    hora = discord.ui.TextInput(
        label="🕐 Hora",
        placeholder="Ejemplo: 20:30",
        required=True,
        max_length=10
    )

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        if not interaction.user.guild_permissions.administrator:

            await interaction.response.send_message(
                "❌ Solo los administradores pueden crear eventos.",
                ephemeral=True
            )

            return

        guild = interaction.guild

        if guild is None:

            await interaction.response.send_message(
                "❌ Este formulario solo funciona dentro de un servidor.",
                ephemeral=True
            )

            return

        canal = discord.utils.get(
            guild.text_channels,
            name=CANAL_EVENTOS
        )

        if canal is None:

            await interaction.response.send_message(
                f"❌ No encuentro el canal **#{CANAL_EVENTOS}**.",
                ephemeral=True
            )

            return

        # ====================================================
        # CREAR ID DEL EVENTO
        # ====================================================

        evento_id = str(
            interaction.id
        )

        evento = {

            "guild_id": guild.id,

            "tipo": self.tipo.value.strip(),

            "fecha": self.fecha.value.strip(),

            "hora": self.hora.value.strip(),

            "creador_id": interaction.user.id,

            "inscritos": [],

            "mensaje_id": None
        }

        # ====================================================
        # CREAR MENSAJE
        # ====================================================

        try:

            mensaje = await canal.send(
                embed=crear_embed_evento(evento),
                view=EventoView(
                    None
                )
            )

            evento["mensaje_id"] = mensaje.id

            # Ahora la vista conoce el mensaje
            await mensaje.edit(
                view=EventoView(
                    mensaje.id
                )
            )

            EVENTOS[evento_id] = evento

            await guardar_eventos()

            await interaction.response.send_message(
                "✅ **Evento creado correctamente.**\n\n"
                f"🎯 **Tipo:** {evento['tipo']}\n"
                f"📅 **Fecha:** {evento['fecha']}\n"
                f"🕐 **Hora:** {evento['hora']}",
                ephemeral=True
            )

            print(
                f"🎉 Evento creado: "
                f"{evento['tipo']} — "
                f"{evento['fecha']} — "
                f"{evento['hora']}"
            )

        except discord.Forbidden:

            await interaction.response.send_message(
                "❌ No tengo permisos para escribir en "
                f"#{CANAL_EVENTOS}.",
                ephemeral=True
            )

        except discord.HTTPException as error:

            print(
                f"❌ Error creando evento: {error}"
            )

            await interaction.response.send_message(
                "❌ Discord no ha permitido crear el evento.",
                ephemeral=True
            )


# ============================================================
# VISTA DEL EVENTO
# ============================================================

class EventoView(discord.ui.View):

    def __init__(
        self,
        mensaje_id
    ):

        super().__init__(
            timeout=None
        )

        self.mensaje_id = mensaje_id

    # ========================================================
    # BUSCAR EVENTO
    # ========================================================

    def obtener_evento(self):

        for evento_id, evento in EVENTOS.items():

            if str(
                evento.get("mensaje_id")
            ) == str(self.mensaje_id):

                return evento_id, evento

        return None, None

    # ========================================================
    # INSCRIBIRSE
    # ========================================================

    @discord.ui.button(
        label="Inscribirme",
        emoji="✅",
        style=discord.ButtonStyle.success,
        custom_id="evento_inscribirse"
    )
    async def inscribirse(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        evento_id, evento = self.obtener_evento()

        if evento is None:

            await interaction.response.send_message(
                "❌ Este evento ya no está disponible.",
                ephemeral=True
            )

            return

        usuario_id = interaction.user.id

        inscritos = evento.setdefault(
            "inscritos",
            []
        )

        if usuario_id in inscritos:

            await interaction.response.send_message(
                "ℹ️ Ya estás inscrito en este evento.",
                ephemeral=True
            )

            return

        inscritos.append(
            usuario_id
        )

        await guardar_eventos()

        canal = interaction.channel

        if canal is not None:

            await actualizar_evento(
                canal,
                evento["mensaje_id"],
                evento
            )

        await interaction.response.send_message(
            "✅ **Te has inscrito en el evento.**",
            ephemeral=True
        )

    # ========================================================
    # CANCELAR
    # ========================================================

    @discord.ui.button(
        label="Cancelar inscripción",
        emoji="❌",
        style=discord.ButtonStyle.secondary,
        custom_id="evento_cancelar"
    )
    async def cancelar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        evento_id, evento = self.obtener_evento()

        if evento is None:

            await interaction.response.send_message(
                "❌ Este evento ya no está disponible.",
                ephemeral=True
            )

            return

        usuario_id = interaction.user.id

        inscritos = evento.setdefault(
            "inscritos",
            []
        )

        if usuario_id not in inscritos:

            await interaction.response.send_message(
                "ℹ️ No estás inscrito en este evento.",
                ephemeral=True
            )

            return

        inscritos.remove(
            usuario_id
        )

        await guardar_eventos()

        canal = interaction.channel

        if canal is not None:

            await actualizar_evento(
                canal,
                evento["mensaje_id"],
                evento
            )

        await interaction.response.send_message(
            "❌ **Has cancelado tu inscripción.**",
            ephemeral=True
        )

    # ========================================================
    # ELIMINAR EVENTO
    # ========================================================

    @discord.ui.button(
        label="Eliminar evento",
        emoji="🗑️",
        style=discord.ButtonStyle.danger,
        custom_id="evento_eliminar"
    )
    async def eliminar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not interaction.user.guild_permissions.administrator:

            await interaction.response.send_message(
                "❌ Solo los administradores pueden eliminar eventos.",
                ephemeral=True
            )

            return

        evento_id, evento = self.obtener_evento()

        if evento is None:

            await interaction.response.send_message(
                "❌ Este evento ya no existe.",
                ephemeral=True
            )

            return

        try:

            mensaje = await interaction.channel.fetch_message(
                evento["mensaje_id"]
            )

            await mensaje.delete()

        except discord.NotFound:
            pass

        except discord.Forbidden:

            await interaction.response.send_message(
                "❌ No tengo permisos para eliminar el evento.",
                ephemeral=True
            )

            return

        except discord.HTTPException as error:

            print(
                f"❌ Error eliminando evento: {error}"
            )

            await interaction.response.send_message(
                "❌ Discord no ha permitido eliminar el evento.",
                ephemeral=True
            )

            return

        # Eliminar de la base de datos
        del EVENTOS[evento_id]

        await guardar_eventos()

        await interaction.response.send_message(
            "🗑️ **Evento eliminado correctamente.**",
            ephemeral=True
        )

        print(
            f"🗑️ Evento eliminado: {evento['tipo']}"
        )


# ============================================================
# PANEL DE ADMINISTRADORES
# ============================================================

class PanelEventosView(discord.ui.View):

    def __init__(self):

        super().__init__(
            timeout=None
        )

    @discord.ui.button(
        label="Crear evento",
        emoji="🛠️",
        style=discord.ButtonStyle.primary,
        custom_id="eventos_crear"
    )
    async def crear_evento(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not interaction.user.guild_permissions.administrator:

            await interaction.response.send_message(
                "❌ Solo los administradores pueden crear eventos.",
                ephemeral=True
            )

            return

        await interaction.response.send_modal(
            CrearEventoModal()
        )


# ============================================================
# COG EVENTOS
# ============================================================

class Eventos(commands.Cog):

    def __init__(
        self,
        bot
    ):

        self.bot = bot

        print(
            "🟢 Eventos.py cargado"
        )

    # ========================================================
    # READY
    # ========================================================

    @commands.Cog.listener()
    async def on_ready(
        self
    ):

        # ====================================================
        # REGISTRAR VISTAS DE EVENTOS EXISTENTES
        # ====================================================

        for evento in EVENTOS.values():

            mensaje_id = evento.get(
                "mensaje_id"
            )

            if mensaje_id:

                self.bot.add_view(
                    EventoView(
                        mensaje_id
                    )
                )

        # ====================================================
        # CREAR PANEL DE ADMINISTRACIÓN
        # ====================================================

        for guild in self.bot.guilds:

            canal = discord.utils.get(
                guild.text_channels,
                name=CANAL_EVENTOS
            )

            if canal is None:

                print(
                    f"❌ No encuentro #{CANAL_EVENTOS} "
                    f"en {guild.name}"
                )

                continue

            try:

                panel_existe = False

                async for mensaje in canal.history(
                    limit=50
                ):

                    if mensaje.author != self.bot.user:
                        continue

                    if not mensaje.embeds:
                        continue

                    if (
                        mensaje.embeds[0].title
                        == "🛠️ PANEL DE EVENTOS"
                    ):

                        panel_existe = True
                        break

                if not panel_existe:

                    embed = discord.Embed(
                        title="🛠️ PANEL DE EVENTOS",
                        description=(
                            "Los administradores pueden crear "
                            "eventos desde el botón de abajo.\n\n"
                            "Los miembros podrán inscribirse "
                            "directamente en cada evento."
                        ),
                        color=discord.Color.gold()
                    )

                    embed.set_footer(
                        text="Panel de administración"
                    )

                    await canal.send(
                        embed=embed,
                        view=PanelEventosView()
                    )

                    print(
                        f"✅ Panel de eventos creado "
                        f"en {guild.name}"
                    )

            except discord.Forbidden:

                print(
                    f"❌ No tengo permisos en "
                    f"#{CANAL_EVENTOS} de {guild.name}"
                )

            except discord.HTTPException as error:

                print(
                    f"❌ Error en eventos: {error}"
                )


# ============================================================
# SETUP
# ============================================================

async def setup(
    bot
):

    # Panel permanente
    bot.add_view(
        PanelEventosView()
    )

    await bot.add_cog(
        Eventos(bot)
    )

    print(
        "✅ Eventos.py instalado correctamente."
    )

