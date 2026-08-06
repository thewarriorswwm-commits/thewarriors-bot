import discord
from discord.ext import commands


# ============================================================
# CONFIGURACIÓN
# ============================================================

CANAL_BIENVENIDA = "bienvenida-🫂"

ROL_NORMAS = "Normas"
ROL_MIEMBRO = "Miembro"


# ============================================================
# OBTENER / CREAR ROL
# ============================================================

async def obtener_rol(
    guild: discord.Guild,
    nombre: str
):

    rol = discord.utils.get(
        guild.roles,
        name=nombre
    )

    if rol is not None:
        return rol

    try:

        return await guild.create_role(
            name=nombre,
            reason=f"The Warriors • Sistema de acceso • {nombre}"
        )

    except discord.Forbidden:

        print(
            f"❌ No puedo crear el rol {nombre}."
        )

        return None

    except discord.HTTPException as error:

        print(
            f"❌ Error creando {nombre}: {error}"
        )

        return None


# ============================================================
# MODAL PARA EL APODO
# ============================================================

class ApodoModal(
    discord.ui.Modal,
    title="📝 Cambiar apodo"
):

    nombre = discord.ui.TextInput(
        label="Nombre dentro del juego",
        placeholder="Escribe tu nombre de Where Winds Meet",
        required=True,
        max_length=32
    )

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        nombre_juego = self.nombre.value.strip()

        if not nombre_juego:

            await interaction.response.send_message(
                "❌ Debes escribir un nombre.",
                ephemeral=True
            )

            return

        guild = interaction.guild

        if guild is None:

            await interaction.response.send_message(
                "❌ Este botón solo funciona dentro del servidor.",
                ephemeral=True
            )

            return

        bot_member = guild.me

        if bot_member is None:

            await interaction.response.send_message(
                "❌ No puedo encontrar al bot.",
                ephemeral=True
            )

            return

        rol_miembro = discord.utils.get(
            guild.roles,
            name=ROL_MIEMBRO
        )

        if rol_miembro is None:

            await interaction.response.send_message(
                "❌ No encuentro el rol **Miembro**.",
                ephemeral=True
            )

            return

        if rol_miembro not in interaction.user.roles:

            await interaction.response.send_message(
                "❌ Primero debes aceptar las normas.",
                ephemeral=True
            )

            return

        if interaction.user.top_role >= bot_member.top_role:

            await interaction.response.send_message(
                "❌ **No puedo cambiar tu apodo.**\n\n"
                "El rol del bot debe estar por encima "
                "de tu rol más alto.",
                ephemeral=True
            )

            return

        try:

            await interaction.user.edit(
                nick=nombre_juego,
                reason="Cambio de apodo mediante The Warriors"
            )

            await interaction.response.send_message(
                "✅ **Apodo cambiado correctamente.**\n\n"
                f"🎮 Tu nombre ahora es: **{nombre_juego}**",
                ephemeral=True
            )

            print(
                f"✅ Apodo cambiado: "
                f"{interaction.user} → {nombre_juego}"
            )

        except discord.Forbidden:

            await interaction.response.send_message(
                "❌ No puedo cambiar tu apodo.\n\n"
                "Comprueba que el rol del bot esté "
                "por encima del usuario.",
                ephemeral=True
            )

        except discord.HTTPException as error:

            print(
                f"❌ Error cambiando apodo: {error}"
            )

            await interaction.response.send_message(
                "❌ Discord no ha podido cambiar el apodo.",
                ephemeral=True
            )


# ============================================================
# BOTONES DE BIENVENIDA
# ============================================================

class BienvenidaView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=None
        )

    # ========================================================
    # ACEPTAR NORMAS
    # ========================================================

    @discord.ui.button(
        label="Aceptar normas",
        emoji="✅",
        style=discord.ButtonStyle.success,
        custom_id="bienvenida_aceptar_normas"
    )
    async def aceptar_normas(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        guild = interaction.guild

        if guild is None:

            await interaction.response.send_message(
                "❌ Este botón solo funciona dentro del servidor.",
                ephemeral=True
            )

            return

        rol_miembro = await obtener_rol(
            guild,
            ROL_MIEMBRO
        )

        if rol_miembro is None:

            await interaction.response.send_message(
                "❌ No puedo configurar el rol **Miembro**.",
                ephemeral=True
            )

            return

        rol_normas = discord.utils.get(
            guild.roles,
            name=ROL_NORMAS
        )

        try:

            if rol_miembro not in interaction.user.roles:

                await interaction.user.add_roles(
                    rol_miembro,
                    reason="Aceptación de las normas de The Warriors"
                )

            if (
                rol_normas is not None
                and rol_normas in interaction.user.roles
            ):

                await interaction.user.remove_roles(
                    rol_normas,
                    reason="Cambio al rol Miembro"
                )

            await interaction.response.send_message(
                "🎉 **¡Normas aceptadas!**\n\n"
                "¡Bienvenido oficialmente a "
                "**The Warriors**! 🫂⚔️\n\n"
                "👤 Tu rol ahora es **Miembro**.\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                "📝 **Ahora puedes poner tu apodo.**\n\n"
                "Pulsa **📝 Cambiar apodo** "
                "y escribe tu nombre de **Where Winds Meet**.",
                ephemeral=True
            )

            print(
                f"✅ {interaction.user} "
                f"ha aceptado las normas → Miembro"
            )

        except discord.Forbidden:

            await interaction.response.send_message(
                "❌ No puedo asignarte el rol **Miembro**.\n\n"
                "Comprueba que el rol del bot esté "
                "por encima del rol Miembro.",
                ephemeral=True
            )

        except discord.HTTPException as error:

            print(
                f"❌ Error asignando Miembro: {error}"
            )

            if not interaction.response.is_done():

                await interaction.response.send_message(
                    "❌ Ha ocurrido un error al aceptar "
                    "las normas.",
                    ephemeral=True
                )

    # ========================================================
    # CAMBIAR APODO
    # ========================================================

    @discord.ui.button(
        label="Cambiar apodo",
        emoji="📝",
        style=discord.ButtonStyle.primary,
        custom_id="bienvenida_cambiar_apodo"
    )
    async def cambiar_apodo(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        guild = interaction.guild

        if guild is None:

            await interaction.response.send_message(
                "❌ Este botón solo funciona dentro del servidor.",
                ephemeral=True
            )

            return

        rol_miembro = discord.utils.get(
            guild.roles,
            name=ROL_MIEMBRO
        )

        if rol_miembro is None:

            await interaction.response.send_message(
                "❌ No encuentro el rol **Miembro**.",
                ephemeral=True
            )

            return

        if rol_miembro not in interaction.user.roles:

            await interaction.response.send_message(
                "❌ Primero debes aceptar las normas "
                "pulsando **✅ Aceptar normas**.",
                ephemeral=True
            )

            return

        await interaction.response.send_modal(
            ApodoModal()
        )


# ============================================================
# COG BIENVENIDA
# ============================================================

class Bienvenida(
    commands.Cog
):

    def __init__(
        self,
        bot
    ):

        self.bot = bot
        self.panel_creado = False

        print(
            "🟢 Bienvenida.py iniciado"
        )

    # ========================================================
    # PANEL AUTOMÁTICO
    # ========================================================

    @commands.Cog.listener()
    async def on_ready(self):

        if self.panel_creado:

            return

        self.panel_creado = True

        for guild in self.bot.guilds:

            canal = discord.utils.get(
                guild.text_channels,
                name=CANAL_BIENVENIDA
            )

            if canal is None:

                print(
                    f"❌ No encuentro #{CANAL_BIENVENIDA} "
                    f"en {guild.name}"
                )

                continue

            existe = False

            try:

                async for mensaje in canal.history(
                    limit=100
                ):

                    if (
                        mensaje.author == self.bot.user
                        and mensaje.embeds
                        and mensaje.embeds[0].title
                        == "🫂 ¡Bienvenido a The Warriors!"
                    ):

                        existe = True

                        break

            except discord.Forbidden:

                print(
                    f"❌ No puedo leer #{CANAL_BIENVENIDA} "
                    f"en {guild.name}"
                )

                continue

            if existe:

                print(
                    f"✅ Panel bienvenida ya existe "
                    f"en {guild.name}"
                )

                continue

            # =================================================
            # EMBED
            # =================================================

            embed = discord.Embed(

                title="🫂 ¡Bienvenido a The Warriors!",

                description=(

                    "**¡Bienvenido a la familia "
                    "The Warriors!** 🫂📢\n\n"

                    "Muchas gracias por unirte a nosotros.\n\n"

                    "Somos una familia que disfruta de "
                    "**Where Winds Meet** juntos. 🎮⚔️\n\n"

                    "━━━━━━━━━━━━━━━━━━━━\n\n"

                    "## 📜 NORMAS DEL GREMIO\n\n"

                    "1️⃣ **🤝 RESPETO**\n"
                    "Respeta a todos los miembros.\n\n"

                    "2️⃣ **💬 BUEN AMBIENTE**\n"
                    "Mantén un ambiente agradable.\n\n"

                    "3️⃣ **⚔️ COMPAÑERISMO**\n"
                    "Ayuda a los demás miembros.\n\n"

                    "4️⃣ **🚫 SPAM**\n"
                    "No hagas spam ni flood.\n\n"

                    "5️⃣ **🔗 ENLACES Y PUBLICIDAD**\n"
                    "No publiques publicidad o enlaces "
                    "sospechosos sin autorización.\n\n"

                    "6️⃣ **🎮 JUEGO LIMPIO**\n"
                    "No se permiten trampas ni exploits.\n\n"

                    "7️⃣ **🎫 TICKETS**\n"
                    "Para asuntos privados utiliza los tickets.\n\n"

                    "8️⃣ **👑 ADMINISTRACIÓN**\n"
                    "Respeta a administradores y moderadores.\n\n"

                    "9️⃣ **📢 CANALES CORRESPONDIENTES**\n"
                    "Utiliza cada canal correctamente.\n\n"

                    "🔟 **❤️ DISFRUTA DEL GREMIO**\n"
                    "Lo importante es disfrutar y ayudarnos.\n\n"

                    "━━━━━━━━━━━━━━━━━━━━\n\n"

                    "## ✅ ACEPTACIÓN DE LAS NORMAS\n\n"

                    "Al pulsar **«✅ Aceptar normas»** "
                    "confirmas que has leído y aceptas "
                    "las normas.\n\n"

                    "👤 Recibirás automáticamente "
                    "el rol **Miembro**.\n\n"

                    "━━━━━━━━━━━━━━━━━━━━\n\n"

                    "## 🏷️ ELIGE TU APODO\n\n"

                    "Después de aceptar las normas, pulsa "
                    "**📝 Cambiar apodo**.\n\n"

                    "Aquí debes poner tu **nombre dentro "
                    "del juego**.\n\n"

                    "🔒 **Tu nombre se introduce de forma "
                    "privada.**\n\n"

                    "🎮 El bot pondrá automáticamente ese "
                    "nombre como tu apodo en el servidor."

                ),

                color=discord.Color.blue()
            )

            embed.set_footer(
                text="The Warriors • Sistema de acceso"
            )

            try:

                await canal.send(
                    embed=embed,
                    view=BienvenidaView()
                )

                print(
                    f"✅ Panel bienvenida creado "
                    f"en {guild.name}"
                )

            except discord.Forbidden:

                print(
                    f"❌ No puedo escribir en "
                    f"#{CANAL_BIENVENIDA} "
                    f"en {guild.name}"
                )

            except discord.HTTPException as error:

                print(
                    f"❌ Error enviando bienvenida: "
                    f"{error}"
                )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    bot.add_view(
        BienvenidaView()
    )

    await bot.add_cog(
        Bienvenida(bot)
    )

    print(
        "✅ Bienvenida.py cargado correctamente."
    )
