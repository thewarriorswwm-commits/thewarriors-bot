import discord
from discord.ui import View, Button
from datetime import datetime


CANAL_LOGS = "logs"
ROL_ADMIN = "administradores"
CATEGORIA_TICKETS = "Tickets"


class TicketControlView(View):

    def __init__(self):
        super().__init__(timeout=None)


    @discord.ui.button(
        label="🔒 Cerrar",
        style=discord.ButtonStyle.red,
        custom_id="cerrar_ticket"
    )
    async def cerrar(
        self,
        interaction: discord.Interaction,
        button: Button
    ):

        await interaction.response.defer(ephemeral=True)

        await interaction.channel.edit(
            name=f"cerrado-{interaction.channel.name}"
        )

        logs = discord.utils.get(
            interaction.guild.text_channels,
            name=CANAL_LOGS
        )

        if logs:
            await logs.send(
                f"🔒 Ticket cerrado: {interaction.channel.mention}"
            )

        await interaction.followup.send(
            "✅ Ticket cerrado.",
            ephemeral=True
        )


    @discord.ui.button(
        label="🗑️ Eliminar",
        style=discord.ButtonStyle.gray,
        custom_id="eliminar_ticket"
    )
    async def eliminar(
        self,
        interaction: discord.Interaction,
        button: Button
    ):

        await interaction.response.defer(ephemeral=True)

        await interaction.channel.delete()
class CrearTicketView(View):

    def __init__(self):
        super().__init__(timeout=None)


    @discord.ui.button(
        label="🎫 Crear Ticket",
        style=discord.ButtonStyle.green,
        custom_id="crear_ticket"
    )
    async def crear_ticket(
        self,
        interaction: discord.Interaction,
        button: Button
    ):

        guild = interaction.guild
        usuario = interaction.user


        existente = discord.utils.get(
            guild.text_channels,
            name=f"ticket-{usuario.name.lower()}"
        )


        if existente:
            await interaction.response.send_message(
                "❌ Ya tienes un ticket abierto.",
                ephemeral=True
            )
            return


        categoria = discord.utils.get(
            guild.categories,
            name=CATEGORIA_TICKETS
        )


        if categoria is None:
            categoria = await guild.create_category(
                CATEGORIA_TICKETS
            )


        rol_admin = discord.utils.get(
            guild.roles,
            name=ROL_ADMIN
        )


        permisos = {
            guild.default_role:
            discord.PermissionOverwrite(
                view_channel=False
            ),

            usuario:
            discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )
        }


        if rol_admin:
            permisos[rol_admin] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )


        canal = await guild.create_text_channel(
            name=f"ticket-{usuario.name.lower()}",
            category=categoria,
            overwrites=permisos
        )
        embed = discord.Embed(
            title="🎫 Nuevo Ticket",
            description=(
                f"Hola {usuario.mention}\n\n"
                "Explica tu problema y un administrador te ayudará."
            ),
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )


        embed.add_field(
            name="Usuario",
            value=usuario.mention,
            inline=False
        )


        await canal.send(
            embed=embed,
            view=TicketControlView()
        )


        logs = discord.utils.get(
            guild.text_channels,
            name=CANAL_LOGS
        )


        if logs:
            await logs.send(
                f"🎫 Nuevo ticket creado\n"
                f"Usuario: {usuario.mention}\n"
                f"Canal: {canal.mention}"
            )


        await interaction.response.send_message(
            f"✅ Ticket creado: {canal.mention}",
            ephemeral=True
        )