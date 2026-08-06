import discord


class GuerraView(discord.ui.View):

    def __init__(self, evento="Guerra"):
        super().__init__(timeout=None)
        self.evento = evento
        self.participantes = {}


    async def registrar(self, interaction, rol):

        self.participantes[interaction.user.id] = {
            "usuario": interaction.user,
            "rol": rol
        }


        canal = discord.utils.get(
            interaction.guild.text_channels,
            name="registro-guerra"
        )


        if canal:

            embed = discord.Embed(
                title="⚔️ Registro de guerra",
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )

            embed.add_field(
                name="📅 Evento",
                value=self.evento,
                inline=False
            )

            embed.add_field(
                name="👤 Jugador",
                value=interaction.user.mention,
                inline=False
            )

            embed.add_field(
                name="🎭 Rol",
                value=rol,
                inline=False
            )


            await canal.send(embed=embed)



        await interaction.response.send_message(
            f"✅ Apuntado como **{rol}** en **{self.evento}**.",
            ephemeral=True
        )



    @discord.ui.button(label="⚔️ DPS", style=discord.ButtonStyle.danger)
    async def dps(self, interaction, button):
        await self.registrar(interaction, "DPS")



    @discord.ui.button(label="🏹 DPS Distancia", style=discord.ButtonStyle.primary)
    async def distancia(self, interaction, button):
        await self.registrar(interaction, "DPS a distancia")



    @discord.ui.button(label="❤️ Healer", style=discord.ButtonStyle.success)
    async def healer(self, interaction, button):
        await self.registrar(interaction, "Healer")



    @discord.ui.button(label="🛡️ Tanque", style=discord.ButtonStyle.secondary)
    async def tanque(self, interaction, button):
        await self.registrar(interaction, "Tanque")



    @discord.ui.button(label="❌ No asistiré", style=discord.ButtonStyle.gray)
    async def no_asistire(self, interaction, button):
        await self.registrar(interaction, "No asistirá")