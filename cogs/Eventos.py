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
        value=evento.get(
            "tipo",
            "Sin especificar"
        ),
        inline=False
    )

    embed.add_field(
        name="📅 Fecha",
        value=evento.get(
            "fecha",
            "Sin especificar"
        ),
        inline=True
    )

    embed.add_field(
        name="🕐 Hora",
        value=evento.get(
            "hora",
            "Sin especificar"
        ),
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
# BUSCAR EVENTO POR MENSAJE
# ============================================================

def buscar_evento_por_mensaje(mensaje_id):

    mensaje_id = str(mensaje_id)

    for evento_id, evento in EVENTOS.items():

        if str(
            evento.get("mensaje_id")
        ) == mensaje_id:

            return evento_id, evento

    return None, None


# ============================================================
# ACTUALIZAR EVENTO
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
            view=EventoView()
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

    except Exception as error:

        print(
            f"❌ Error inesperado actualizando evento: {error}"
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

        evento = {

            "guild_id": guild.id,

            "tipo": self.tipo.value.strip(),

            "fecha": self.fecha.value.strip(),

            "hora": self.hora.value.strip(),

            "creador_id": interaction.user.id,

            "inscritos": [],

            "mensaje_id": None
        }

        try:

            # ==================================================
            # CREAR MENSAJE
            # ==================================================

            mensaje = await canal.send(
                embed=crear_embed_evento(evento),
                view=EventoView()
            )

            evento["mensaje_id"] = mensaje.id

            # ==================================================
            # GUARDAR EVENTO
            # ==================================================

            evento_id = str(
                mensaje.id
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

            if not interaction.response.is_done():

                await interaction.response.send_message(
                    "❌ No tengo permisos para escribir "
                    f"en #{CANAL_EVENTOS}.",
                    ephemeral=True
                )

        except discord.HTTPException as error:

            print(
                f"❌ Error creando evento: {error}"
            )

            if not interaction.response.is_done():

                await interaction.response.send_message(
                    "❌ Discord no ha permitido crear el evento.",
                    ephemeral=True
                )

        except Exception as error:

            print(
                f"❌ Error inesperado creando evento: {error}"
            )

            if not interaction.response.is_done():

                await interaction.response.send_message(
                    "❌ Ha ocurrido un error creando el evento.",
                    ephemeral=True
                )


# ============================================================
# VISTA DE LOS EVENTOS
# ============================================================

class EventoView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=None
        )


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

        mensaje = interaction.message

        if mensaje is None:

            await interaction.response.send_message(
                "❌ No puedo localizar este evento.",
                ephemeral=True
            )

            return

        evento_id, evento = buscar_evento_por_mensaje(
            mensaje.id
        )

        if evento is None:

            await interaction.response.send_message(
                "❌ Este evento ya no está disponible.",
                ephemeral=True
            )

            return

        usuario_id = interaction.user.id

        # ====================================================
        # BLOQUEAR CAMBIOS SIMULTÁNEOS
        # ====================================================

        async with LOCK_EVENTOS:

            inscritos = evento.setdefault(
                "inscritos",
                []
            )

            # Convertimos a int para evitar problemas
            # si algún ID antiguo está guardado como texto.
            inscritos = [
                int(uid)
                for uid in inscritos
            ]

            evento["inscritos"] = inscritos

            if usuario_id in inscritos:

                await interaction.response.send_message(
                    "ℹ️ Ya estás inscrito en este evento.",
                    ephemeral=True
                )

                return

            inscritos.append(
                usuario_id
            )

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
                    f"❌ Error guardando inscripción: {error}"
                )

                inscritos.remove(
                    usuario_id
                )

                await interaction.response.send_message(
                    "❌ No se pudo guardar tu inscripción.",
                    ephemeral=True
                )

                return

        # ====================================================
        # RESPONDER
        # ====================================================

        await interaction.response.send_message(
            "✅ **Te has inscrito en el evento.**",
            ephemeral=True
        )

        # ====================================================
        # ACTUALIZAR MENSAJE
        # ====================================================

        await actualizar_evento(
            interaction.channel,
            mensaje.id,
            evento
        )


    # ========================================================
    # CANCELAR INSCRIPCIÓN
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

        mensaje = interaction.message

        if mensaje is None:

            await interaction.response.send_message(
                "❌ No puedo localizar este evento.",
                ephemeral=True
            )

            return

        evento_id, evento = buscar_evento_por_mensaje(
            mensaje.id
        )

        if evento is None:

            await interaction.response.send_message(
                "❌ Este evento ya no está disponible.",
                ephemeral=True
            )

            return

        usuario_id = interaction.user.id

        # ====================================================
        # BLOQUEAR CAMBIOS SIMULTÁNEOS
        # ====================================================

        async with LOCK_EVENTOS:

            inscritos = evento.setdefault(
                "inscritos",
                []
            )

            inscritos = [
                int(uid)
                for uid in inscritos
            ]

            evento["inscritos"] = inscritos

            if usuario_id not in inscritos:

                await interaction.response.send_message(
                    "ℹ️ No estás inscrito en este evento.",
                    ephemeral=True
                )

                return

            inscritos.remove(
                usuario_id
            )

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
                    f"❌ Error guardando cancelación: {error}"
                )

                inscritos.append(
                    usuario_id
                )

                await interaction.response.send_message(
                    "❌ No se pudo cancelar tu inscripción.",
                    ephemeral=True
                )

                return

        # ====================================================
        # RESPONDER
        # ====================================================

        await interaction.response.send_message(
            "❌ **Has cancelado tu inscripción.**",
            ephemeral=True
        )

        # ====================================================
        # ACTUALIZAR MENSAJE
        # ====================================================

        await actualizar_evento(
            interaction.channel,
            mensaje.id,
            evento
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

        mensaje = interaction.message

        if mensaje is None:

            await interaction.response.send_message(
                "❌ No puedo localizar este evento.",
                ephemeral=True
            )

            return

        evento_id, evento = buscar_evento_por_mensaje(
            mensaje.id
        )

        if evento is None:

            await interaction.response.send_message(
                "❌ Este evento ya no existe.",
                ephemeral=True
            )

            return

        # ====================================================
        # RESPONDER ANTES DE BORRAR
        # ====================================================

        await interaction.response.send_message(
            "🗑️ **Evento eliminado correctamente.**",
            ephemeral=True
        )

        # ====================================================
        # BORRAR MENSAJE
        # ====================================================

        try:

            await mensaje.delete()

        except discord.NotFound:

            pass

        except discord.Forbidden:

            print(
                "❌ No tengo permisos para eliminar el evento."
            )

            return

        except discord.HTTPException as error:

            print(
                f"❌ Error eliminando evento: {error}"
            )

            return

        # ====================================================
        # BORRAR DE LA BASE DE DATOS
        # ====================================================

        async with LOCK_EVENTOS:

            EVENTOS.pop(
                evento_id,
                None
            )

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
                    f"❌ Error guardando eliminación: {error}"
                )

        print(
            f"🗑️ Evento eliminado: "
            f"{evento.get('tipo', 'Evento')}"
        )


# ============================================================
# PANEL DE ADMINISTRADORES
# ============================================================

class PanelEventosView(
    discord.ui.View
):

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

class Eventos(
    commands.Cog
):

    def __init__(
        self,
        bot
    ):

        self.bot = bot

        print(
            "🟢 Eventos.py cargado"
        )


# ============================================================
# SETUP
# ============================================================

async def setup(
    bot
):

    # ========================================================
    # REGISTRAR VISTAS PERSISTENTES
    # ========================================================

    bot.add_view(
        PanelEventosView()
    )

    bot.add_view(
        EventoView()
    )

    # ========================================================
    # CARGAR COG
    # ========================================================

    await bot.add_cog(
        Eventos(bot)
    )

    print(
        "✅ Eventos.py instalado correctamente."
    )
