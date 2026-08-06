import discord
from discord.ext import commands
from zoneinfo import ZoneInfo
from datetime import datetime


# ============================================================
# CONFIGURACIÓN
# ============================================================

CANAL_GUERRAS = "guerras-⚔️"
CANAL_REGISTRO = "registro-guerra-📋"

ZONA_HORARIA = ZoneInfo("Europe/Madrid")


# ============================================================
# VISTA DEL PANEL
# ============================================================

class GuerraView(discord.ui.View):

    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(
        label="Registrar guerra",
        emoji="⚔️",
        style=discord.ButtonStyle.danger,
        custom_id="guerra_registrar"
    )
    async def registrar_guerra(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_modal(
            GuerraModal(self.cog)
        )


# ============================================================
# MODAL DE REGISTRO
# ============================================================

class GuerraModal(
    discord.ui.Modal,
    title="Registrar guerra"
):

    rival = discord.ui.TextInput(
        label="Rival",
        placeholder="Nombre del rival",
        required=True,
        max_length=100
    )

    fecha = discord.ui.TextInput(
        label="Fecha",
        placeholder="Ejemplo: 06/08/2026",
        required=True,
        max_length=20
    )

    hora = discord.ui.TextInput(
        label="Hora",
        placeholder="Ejemplo: 22:00",
        required=True,
        max_length=10
    )

    jugadores = discord.ui.TextInput(
        label="Jugadores",
        placeholder="Ejemplo: 10",
        required=True,
        max_length=10
    )

    notas = discord.ui.TextInput(
        label="Notas",
        placeholder="Información adicional",
        required=False,
        style=discord.TextStyle.paragraph,
        max_length=500
    )

    def __init__(self, cog):
        super().__init__()
        self.cog = cog

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        # ====================================================
        # FECHA Y HORA
        # ====================================================

        try:

            fecha_hora = datetime.strptime(
                f"{self.fecha.value.strip()} "
                f"{self.hora.value.strip()}",
                "%d/%m/%Y %H:%M"
            ).replace(
                tzinfo=ZONA_HORARIA
            )

        except ValueError:

            await interaction.response.send_message(
                "❌ Fecha u hora incorrectas.\n"
                "Ejemplo: `06/08/2026` y `22:00`.",
                ephemeral=True
            )

            return

        # ====================================================
        # COMPROBAR FECHA
        # ====================================================

        ahora = datetime.now(
            ZONA_HORARIA
        )

        if fecha_hora <= ahora:

            await interaction.response.send_message(
                "❌ La fecha de la guerra debe ser futura.",
                ephemeral=True
            )

            return

        # ====================================================
        # DATOS
        # ====================================================

        datos = {
            "rival": self.rival.value.strip(),
            "fecha": fecha_hora,
            "jugadores": self.jugadores.value.strip(),
            "notas": self.notas.value.strip()
        }

        # ====================================================
        # GUARDAR
        # ====================================================

        self.cog.guerras.append(datos)

        # ====================================================
        # RESPUESTA
        # ====================================================

        await interaction.response.send_message(
            "✅ **Guerra registrada correctamente.**\n"
            "📋 Se enviará automáticamente al registro.",
            ephemeral=True
        )

        # ====================================================
        # REGISTRO AUTOMÁTICO
        # ====================================================

        try:

            await self.cog.enviar_registro(
                interaction.guild,
                interaction.user,
                datos
            )

        except Exception as e:

            print(
                f"[GUERRAS] ERROR REGISTRO: {e}"
            )

        # ====================================================
        # ACTUALIZAR PANEL
        # ====================================================

        try:

            await self.cog.actualizar_guerras(
                interaction.guild
            )

        except Exception as e:

            print(
                f"[GUERRAS] ERROR PANEL: {e}"
            )


# ============================================================
# COG
# ============================================================

class Guerras(commands.Cog):

    def __init__(
        self,
        bot
    ):

        self.bot = bot

        self.guerras = []

    # ========================================================
    # BUSCAR CANAL
    # ========================================================

    def obtener_canal(
        self,
        guild,
        nombre
    ):

        if guild is None:
            return None

        # Búsqueda exacta
        canal = discord.utils.get(
            guild.text_channels,
            name=nombre
        )

        if canal:
            return canal

        # Segunda búsqueda
        for canal in guild.text_channels:

            if canal.name.strip() == nombre.strip():

                return canal

        return None

    # ========================================================
    # ENVIAR REGISTRO AUTOMÁTICAMENTE
    # ========================================================

    async def enviar_registro(
        self,
        guild,
        usuario,
        guerra
    ):

        if guild is None:
            return

        canal = self.obtener_canal(
            guild,
            CANAL_REGISTRO
        )

        if canal is None:

            print(
                f"[GUERRAS] ❌ NO EXISTE: "
                f"{CANAL_REGISTRO}"
            )

            return

        # ====================================================
        # PERMISOS
        # ====================================================

        bot_member = guild.me

        if bot_member is None:
            return

        permisos = canal.permissions_for(
            bot_member
        )

        if not permisos.view_channel:

            print(
                f"[GUERRAS] ❌ NO PUEDE VER: "
                f"{CANAL_REGISTRO}"
            )

            return

        if not permisos.send_messages:

            print(
                f"[GUERRAS] ❌ NO PUEDE ESCRIBIR: "
                f"{CANAL_REGISTRO}"
            )

            return

        # ====================================================
        # FECHA
        # ====================================================

        fecha = guerra["fecha"].astimezone(
            ZONA_HORARIA
        )

        # ====================================================
        # EMBED
        # ====================================================

        embed = discord.Embed(
            title="📋 Registro de guerra",
            description="⚔️ **Nueva guerra registrada**",
            timestamp=datetime.now(
                ZONA_HORARIA
            )
        )

        embed.add_field(
            name="⚔️ Rival",
            value=guerra["rival"],
            inline=False
        )

        embed.add_field(
            name="📅 Fecha",
            value=fecha.strftime(
                "%d/%m/%Y"
            ),
            inline=True
        )

        embed.add_field(
            name="🕐 Hora",
            value=fecha.strftime(
                "%H:%M"
            ),
            inline=True
        )

        embed.add_field(
            name="👥 Jugadores",
            value=guerra["jugadores"],
            inline=True
        )

        if guerra["notas"]:

            embed.add_field(
                name="📝 Notas",
                value=guerra["notas"],
                inline=False
            )

        embed.add_field(
            name="👤 Registrada por",
            value=usuario.mention,
            inline=False
        )

        embed.set_footer(
            text="The Warriors • Registro de guerras"
        )

        # ====================================================
        # ENVIAR
        # ====================================================

        try:

            await canal.send(
                embed=embed
            )

            print(
                f"[GUERRAS] ✅ REGISTRO ENVIADO A "
                f"#{CANAL_REGISTRO}"
            )

        except discord.Forbidden:

            print(
                f"[GUERRAS] ❌ SIN PERMISOS EN "
                f"#{CANAL_REGISTRO}"
            )

        except discord.HTTPException as e:

            print(
                f"[GUERRAS] ❌ ERROR DISCORD: {e}"
            )

    # ========================================================
    # ACTUALIZAR PANEL
    # ========================================================

    async def actualizar_guerras(
        self,
        guild
    ):

        if guild is None:

            print(
                "[GUERRAS] ❌ GUILD ES NONE"
            )

            return False

        # ====================================================
        # BUSCAR CANAL
        # ====================================================

        canal = self.obtener_canal(
            guild,
            CANAL_GUERRAS
        )

        if canal is None:

            print(
                f"[GUERRAS] ❌ NO EXISTE EL CANAL: "
                f"{CANAL_GUERRAS}"
            )

            return False

        # ====================================================
        # COMPROBAR PERMISOS
        # ====================================================

        bot_member = guild.me

        if bot_member is None:

            print(
                "[GUERRAS] ❌ NO SE ENCUENTRA EL BOT"
            )

            return False

        permisos = canal.permissions_for(
            bot_member
        )

        if not permisos.view_channel:

            print(
                f"[GUERRAS] ❌ NO PUEDE VER "
                f"#{CANAL_GUERRAS}"
            )

            return False

        if not permisos.send_messages:

            print(
                f"[GUERRAS] ❌ NO PUEDE ESCRIBIR "
                f"#{CANAL_GUERRAS}"
            )

            return False

        # ====================================================
        # BORRAR PANELES ANTERIORES DEL BOT
        # ====================================================

        try:

            async for mensaje in canal.history(
                limit=50
            ):

                if mensaje.author == self.bot.user:

                    try:

                        await mensaje.delete()

                    except (
                        discord.Forbidden,
                        discord.HTTPException
                    ):

                        pass

        except discord.Forbidden:

            print(
                f"[GUERRAS] ⚠️ NO PUEDE LEER HISTORIAL "
                f"#{CANAL_GUERRAS}"
            )

        except Exception as e:

            print(
                f"[GUERRAS] ⚠️ ERROR HISTORIAL: {e}"
            )

        # ====================================================
        # CREAR EMBED
        # ====================================================

        embed = discord.Embed(
            title="⚔️ Guerras",
            description=(
                "Aquí puedes registrar las próximas guerras "
                "de **The Warriors**.\n\n"
                "Pulsa **Registrar guerra** para añadir una."
            )
        )

        # ====================================================
        # MOSTRAR GUERRAS
        # ====================================================

        if self.guerras:

            for numero, guerra in enumerate(
                self.guerras,
                start=1
            ):

                fecha = guerra["fecha"].astimezone(
                    ZONA_HORARIA
                )

                texto = (
                    f"⚔️ **Rival:** {guerra['rival']}\n"
                    f"📅 **Fecha:** "
                    f"{fecha.strftime('%d/%m/%Y')}\n"
                    f"🕐 **Hora:** "
                    f"{fecha.strftime('%H:%M')}\n"
                    f"👥 **Jugadores:** "
                    f"{guerra['jugadores']}"
                )

                if guerra["notas"]:

                    texto += (
                        f"\n📝 **Notas:** "
                        f"{guerra['notas']}"
                    )

                embed.add_field(
                    name=f"⚔️ Guerra #{numero}",
                    value=texto,
                    inline=False
                )

        else:

            embed.add_field(
                name="📭 No hay guerras registradas",
                value=(
                    "Todavía no hay ninguna guerra programada."
                ),
                inline=False
            )

        # ====================================================
        # ENVIAR PANEL
        # ====================================================

        try:

            await canal.send(
                embed=embed,
                view=GuerraView(self)
            )

            print(
                f"[GUERRAS] ✅ PANEL ENVIADO A "
                f"#{CANAL_GUERRAS}"
            )

            return True

        except discord.Forbidden:

            print(
                f"[GUERRAS] ❌ DISCORD RECHAZÓ EL ENVÍO "
                f"EN #{CANAL_GUERRAS}"
            )

            return False

        except discord.HTTPException as e:

            print(
                f"[GUERRAS] ❌ ERROR DISCORD PANEL: {e}"
            )

            return False

        except Exception as e:

            print(
                f"[GUERRAS] ❌ ERROR PANEL: {e}"
            )

            return False

    # ========================================================
    # COMANDO !GUERRAS
    # ========================================================

    @commands.command(
        name="guerras"
    )
    @commands.has_permissions(
        administrator=True
    )
    async def guerras_command(
        self,
        ctx
    ):

        try:

            resultado = await self.actualizar_guerras(
                ctx.guild
            )

            if resultado:

                await ctx.send(
                    "✅ **Panel de guerras enviado correctamente.**",
                    delete_after=5
                )

            else:

                await ctx.send(
                    "❌ **No se pudo enviar el panel.**\n"
                    "Mira la consola del bot para ver el motivo.",
                    delete_after=15
                )

        except Exception as e:

            print(
                f"[GUERRAS] ❌ ERROR EN !GUERRAS: {e}"
            )

            try:

                await ctx.send(
                    f"❌ **Error en `!guerras`:**\n"
                    f"```{e}```",
                    delete_after=15
                )

            except discord.HTTPException:
                pass

    # ========================================================
    # ERROR DEL COMANDO
    # ========================================================

    @guerras_command.error
    async def guerras_command_error(
        self,
        ctx,
        error
    ):

        if isinstance(
            error,
            commands.MissingPermissions
        ):

            await ctx.send(
                "❌ No tienes permisos para usar `!guerras`.",
                delete_after=10
            )

            return

        print(
            f"[GUERRAS] ❌ ERROR DEL COMANDO: {error}"
        )

        try:

            await ctx.send(
                f"❌ Error en `!guerras`:\n"
                f"```{error}```",
                delete_after=15
            )

        except discord.HTTPException:
            pass


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        Guerras(bot)
    )

