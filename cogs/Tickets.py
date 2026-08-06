import discord
from discord.ext import commands
from io import BytesIO


# ============================================================
# CONFIGURACIÓN
# ============================================================

CANAL_TICKETS = "tickets-📨"
CATEGORIA_TICKETS = "TICKETS"
CANAL_LOGS = "logs"


# ============================================================
# TRANSCRIPCIÓN
# ============================================================

async def crear_transcripcion(canal):

    lineas = []

    async for mensaje in canal.history(
        limit=None,
        oldest_first=True
    ):

        fecha = mensaje.created_at.strftime(
            "%d/%m/%Y %H:%M"
        )

        contenido = mensaje.content or "[Sin texto]"

        lineas.append(
            f"[{fecha}] {mensaje.author} "
            f"({mensaje.author.id}): {contenido}"
        )

    if not lineas:
        return "No hay mensajes en este ticket."

    return "\n".join(lineas)


# ============================================================
# ASEGURAR CATEGORÍA Y CANAL
# ============================================================

async def asegurar_tickets(guild):

    categoria = discord.utils.get(
        guild.categories,
        name=CATEGORIA_TICKETS
    )

    if categoria is None:

        categoria = await guild.create_category(
            CATEGORIA_TICKETS,
            reason="Crear categoría automática de tickets"
        )

        print(
            f"✅ Categoría TICKETS creada en {guild.name}"
        )

    canal = discord.utils.get(
        guild.text_channels,
        name=CANAL_TICKETS
    )

    if canal is None:

        canal = await guild.create_text_channel(
            CANAL_TICKETS,
            reason="Crear canal automático de tickets"
        )

        print(
            f"✅ Canal #{CANAL_TICKETS} creado en {guild.name}"
        )

    return categoria, canal


# ============================================================
# CONFIRMACIÓN PARA ELIMINAR
# ============================================================

class ConfirmarEliminarView(discord.ui.View):

    def __init__(self):

        super().__init__(
            timeout=60
        )

    @discord.ui.button(
        label="✅ Sí, eliminar",
        style=discord.ButtonStyle.danger
    )
    async def confirmar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        canal = interaction.channel
        guild = interaction.guild

        if not isinstance(
            canal,
            discord.TextChannel
        ):
            return

        await interaction.response.send_message(
            "🗑️ Guardando transcripción y eliminando ticket..."
        )

        # ----------------------------------------------------
        # CREAR TRANSCRIPCIÓN
        # ----------------------------------------------------

        try:

            texto = await crear_transcripcion(
                canal
            )

            logs = discord.utils.get(
                guild.text_channels,
                name=CANAL_LOGS
            )

            if logs:

                archivo = discord.File(
                    BytesIO(
                        texto.encode("utf-8")
                    ),
                    filename=(
                        f"transcripcion-{canal.name}.txt"
                    )
                )

                await logs.send(
                    "🗑️ **Ticket eliminado**\n"
                    f"📁 Canal: `{canal.name}`\n"
                    f"👤 Eliminado por: "
                    f"{interaction.user.mention}",
                    file=archivo
                )

        except Exception as e:

            print(
                f"❌ Error guardando transcripción: {e}"
            )

        # ----------------------------------------------------
        # ELIMINAR CANAL
        # ----------------------------------------------------

        try:

            await canal.delete(
                reason=(
                    f"Ticket eliminado por "
                    f"{interaction.user}"
                )
            )

        except discord.Forbidden:

            print(
                "❌ No tengo permiso para eliminar "
                "el ticket."
            )

        except discord.HTTPException as e:

            print(
                f"❌ Error eliminando ticket: {e}"
            )

    @discord.ui.button(
        label="❌ Cancelar",
        style=discord.ButtonStyle.secondary
    )
    async def cancelar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.edit_message(
            content="❌ Eliminación cancelada. "
                    "El ticket no se ha borrado.",
            view=None
        )

        self.stop()


# ============================================================
# PANEL PRINCIPAL
# ============================================================

class TicketPanelView(discord.ui.View):

    def __init__(self):

        super().__init__(
            timeout=None
        )

    @discord.ui.button(
        label="📨 Crear ticket",
        style=discord.ButtonStyle.green,
        custom_id="crear_ticket"
    )
    async def crear_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        guild = interaction.guild
        usuario = interaction.user

        if guild is None:
            return

        try:

            categoria, _ = await asegurar_tickets(
                guild
            )

        except discord.Forbidden:

            await interaction.response.send_message(
                "❌ No tengo permisos para crear "
                "la categoría o los canales.",
                ephemeral=True
            )

            return

        except discord.HTTPException as e:

            print(
                f"❌ Error preparando tickets: {e}"
            )

            await interaction.response.send_message(
                "❌ Discord no ha podido preparar "
                "el sistema de tickets.",
                ephemeral=True
            )

            return

        # ----------------------------------------------------
        # COMPROBAR TICKET EXISTENTE
        # ----------------------------------------------------

        nombre_ticket = f"ticket-{usuario.id}"

        existente = discord.utils.get(
            guild.text_channels,
            name=nombre_ticket
        )

        if existente:

            await interaction.response.send_message(
                f"❌ Ya tienes un ticket abierto: "
                f"{existente.mention}",
                ephemeral=True
            )

            return

        # ----------------------------------------------------
        # PERMISOS
        # ----------------------------------------------------

        overwrites = {

            guild.default_role:
                discord.PermissionOverwrite(
                    view_channel=False
                ),

            usuario:
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    attach_files=True,
                    embed_links=True
                )
        }

        # Administradores
        for miembro in guild.members:

            if miembro.guild_permissions.administrator:

                overwrites[miembro] = (
                    discord.PermissionOverwrite(
                        view_channel=True,
                        send_messages=True,
                        read_message_history=True,
                        attach_files=True,
                        embed_links=True
                    )
                )

        # Bot
        if guild.me:

            overwrites[guild.me] = (
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    attach_files=True,
                    embed_links=True,
                    manage_channels=True,
                    manage_messages=True
                )
            )

        # ----------------------------------------------------
        # CREAR TICKET
        # ----------------------------------------------------

        try:

            canal = await guild.create_text_channel(
                name=nombre_ticket,
                category=categoria,
                overwrites=overwrites,
                reason=f"Ticket creado por {usuario}"
            )

        except discord.Forbidden:

            await interaction.response.send_message(
                "❌ No tengo permisos para crear "
                "el canal del ticket.",
                ephemeral=True
            )

            return

        except discord.HTTPException as e:

            print(
                f"❌ Error creando ticket: {e}"
            )

            await interaction.response.send_message(
                "❌ Discord no ha podido crear "
                "el ticket.",
                ephemeral=True
            )

            return

        # ----------------------------------------------------
        # PANEL DEL TICKET
        # ----------------------------------------------------

        embed = discord.Embed(
            title="📨 Ticket de soporte",
            description=(
                f"Hola {usuario.mention} 👋\n\n"
                "Tu ticket ha sido creado correctamente.\n\n"
                "🛡️ Un administrador atenderá "
                "tu solicitud lo antes posible.\n\n"
                "🔒 **Cerrar** — Cierra el ticket.\n"
                "🔓 **Reabrir** — Reabre el ticket.\n"
                "📄 **Transcripción** — Guarda una copia.\n"
                "🗑️ **Eliminar** — Pide confirmación "
                "antes de borrar."
            ),
            color=discord.Color.blue()
        )

        embed.set_footer(
            text="The Warriors • Sistema de tickets"
        )

        await canal.send(
            content=usuario.mention,
            embed=embed,
            view=TicketView()
        )

        await interaction.response.send_message(
            f"✅ Ticket creado: {canal.mention}",
            ephemeral=True
        )

        # ----------------------------------------------------
        # LOG
        # ----------------------------------------------------

        logs = discord.utils.get(
            guild.text_channels,
            name=CANAL_LOGS
        )

        if logs:

            await logs.send(
                "📨 **Ticket creado**\n"
                f"👤 Usuario: {usuario.mention}\n"
                f"📁 Canal: {canal.mention}"
            )


# ============================================================
# VISTA DEL TICKET
# ============================================================

class TicketView(discord.ui.View):

    def __init__(self):

        super().__init__(
            timeout=None
        )

    # ========================================================
    # CERRAR
    # ========================================================

    @discord.ui.button(
        label="🔒 Cerrar",
        style=discord.ButtonStyle.secondary,
        custom_id="cerrar_ticket"
    )
    async def cerrar_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        canal = interaction.channel

        if not isinstance(
            canal,
            discord.TextChannel
        ):
            return

        await canal.set_permissions(
            interaction.user,
            send_messages=False
        )

        await interaction.response.send_message(
            "🔒 **Ticket cerrado.**\n\n"
            "Puedes utilizar **🔓 Reabrir** "
            "si necesitas continuar."
        )

    # ========================================================
    # REABRIR
    # ========================================================

    @discord.ui.button(
        label="🔓 Reabrir",
        style=discord.ButtonStyle.success,
        custom_id="reabrir_ticket"
    )
    async def reabrir_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        canal = interaction.channel

        if not isinstance(
            canal,
            discord.TextChannel
        ):
            return

        await canal.set_permissions(
            interaction.user,
            view_channel=True,
            send_messages=True,
            read_message_history=True,
            attach_files=True,
            embed_links=True
        )

        await interaction.response.send_message(
            "🔓 **Ticket reabierto.**"
        )

    # ========================================================
    # TRANSCRIPCIÓN
    # ========================================================

    @discord.ui.button(
        label="📄 Transcripción",
        style=discord.ButtonStyle.primary,
        custom_id="transcripcion_ticket"
    )
    async def transcripcion_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        canal = interaction.channel

        if not isinstance(
            canal,
            discord.TextChannel
        ):
            return

        await interaction.response.defer(
            ephemeral=True
        )

        try:

            texto = await crear_transcripcion(
                canal
            )

            archivo = discord.File(
                BytesIO(
                    texto.encode("utf-8")
                ),
                filename=(
                    f"transcripcion-{canal.name}.txt"
                )
            )

            await interaction.followup.send(
                "📄 Aquí tienes la transcripción.",
                file=archivo,
                ephemeral=True
            )

        except Exception as e:

            print(
                f"❌ Error creando transcripción: {e}"
            )

            await interaction.followup.send(
                "❌ No se pudo crear "
                "la transcripción.",
                ephemeral=True
            )

    # ========================================================
    # ELIMINAR
    # ========================================================

    @discord.ui.button(
        label="🗑️ Eliminar",
        style=discord.ButtonStyle.danger,
        custom_id="eliminar_ticket"
    )
    async def eliminar_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_message(
            "⚠️ **¿Seguro que quieres eliminar este ticket?**\n\n"
            "La conversación se guardará en `#logs` "
            "antes de eliminar el canal.",
            view=ConfirmarEliminarView()
        )


# ============================================================
# COG TICKETS
# ============================================================

class Tickets(commands.Cog):

    def __init__(
        self,
        bot
    ):

        self.bot = bot

        print(
            "🟢 Tickets.py iniciado"
        )

    # ========================================================
    # PANEL AUTOMÁTICO
    # ========================================================

    async def crear_panel_automatico(
        self
    ):

        for guild in self.bot.guilds:

            try:

                categoria, canal = await asegurar_tickets(
                    guild
                )

            except Exception as e:

                print(
                    f"❌ Error en tickets de "
                    f"{guild.name}: {e}"
                )

                continue

            # ------------------------------------------------
            # COMPROBAR SI YA EXISTE EL PANEL
            # ------------------------------------------------

            panel_existe = False

            try:

                async for mensaje in canal.history(
                    limit=50
                ):

                    if mensaje.author != self.bot.user:
                        continue

                    if not mensaje.embeds:
                        continue

                    if (
                        mensaje.embeds[0].title
                        == "📨 SOPORTE"
                    ):

                        panel_existe = True
                        break

            except discord.Forbidden:

                print(
                    f"❌ No puedo leer "
                    f"#{CANAL_TICKETS}"
                )

                continue

            if panel_existe:

                print(
                    f"ℹ️ Panel ya existe en "
                    f"{guild.name}"
                )

                continue

            # ------------------------------------------------
            # CREAR PANEL
            # ------------------------------------------------

            embed = discord.Embed(
                title="📨 SOPORTE",
                description=(
                    "¿Necesitas ayuda?\n\n"
                    "Pulsa **📨 Crear ticket** para abrir "
                    "un canal privado con el equipo.\n\n"
                    "🔒 El ticket será visible únicamente "
                    "para ti, administradores y el bot."
                ),
                color=discord.Color.blue()
            )

            embed.set_footer(
                text="The Warriors • Sistema de tickets"
            )

            try:

                await canal.send(
                    embed=embed,
                    view=TicketPanelView()
                )

                print(
                    f"✅ Panel automático creado "
                    f"en {guild.name}"
                )

            except discord.Forbidden:

                print(
                    f"❌ No puedo escribir en "
                    f"#{CANAL_TICKETS}"
                )

    # ========================================================
    # AL ARRANCAR
    # ========================================================

    @commands.Cog.listener()
    async def on_ready(
        self
    ):

        print(
            "📨 Comprobando sistema de tickets..."
        )

        await self.crear_panel_automatico()

        print(
            "✅ Sistema de tickets preparado."
        )


# ============================================================
# SETUP
# ============================================================

async def setup(
    bot
):

    bot.add_view(
        TicketPanelView()
    )

    bot.add_view(
        TicketView()
    )

    await bot.add_cog(
        Tickets(bot)
    )

    print(
        "✅ Tickets.py cargado correctamente."
    )