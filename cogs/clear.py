import discord
from discord.ext import commands
from discord import app_commands


# ============================================================
# CLEAR
# ============================================================

class Clear(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        print("🟢 Clear.py iniciado")


    # ========================================================
    # COMANDO /CLEAR
    # SOLO ADMINISTRADORES
    # ========================================================

    @commands.hybrid_command(
        name="clear",
        description="Borra mensajes del canal."
    )
    @app_commands.default_permissions(
        administrator=True
    )
    @commands.has_permissions(
        administrator=True
    )
    @commands.bot_has_permissions(
        manage_messages=True
    )
    async def clear(
        self,
        ctx,
        cantidad: int
    ):

        # ====================================================
        # COMPROBAR SERVIDOR
        # ====================================================

        if ctx.guild is None:

            if ctx.interaction:

                await ctx.send(
                    "❌ Este comando solo puede utilizarse "
                    "en un servidor.",
                    ephemeral=True
                )

            else:

                await ctx.send(
                    "❌ Este comando solo puede utilizarse "
                    "en un servidor.",
                    delete_after=5
                )

            return


        # ====================================================
        # COMPROBAR CANTIDAD
        # ====================================================

        if cantidad < 1:

            if ctx.interaction:

                await ctx.send(
                    "❌ La cantidad debe ser mayor que **0**.",
                    ephemeral=True
                )

            else:

                await ctx.send(
                    "❌ La cantidad debe ser mayor que **0**.",
                    delete_after=5
                )

            return


        if cantidad > 100:

            if ctx.interaction:

                await ctx.send(
                    "❌ No puedes borrar más de "
                    "**100 mensajes** a la vez.",
                    ephemeral=True
                )

            else:

                await ctx.send(
                    "❌ No puedes borrar más de "
                    "**100 mensajes** a la vez.",
                    delete_after=5
                )

            return


        # ====================================================
        # BORRAR MENSAJES
        # ====================================================

        try:

            mensajes = await ctx.channel.purge(
                limit=cantidad
            )

            cantidad_borrada = len(mensajes)


            # =================================================
            # RESPUESTA PRIVADA
            # =================================================

            if ctx.interaction:

                await ctx.send(
                    f"🧹 Se han eliminado "
                    f"**{cantidad_borrada} mensajes**.",
                    ephemeral=True
                )

            else:

                try:

                    await ctx.message.delete()

                except discord.Forbidden:

                    pass

                await ctx.send(
                    f"🧹 Se han eliminado "
                    f"**{cantidad_borrada} mensajes**.",
                    delete_after=5
                )


        except discord.Forbidden:

            if ctx.interaction:

                await ctx.send(
                    "❌ No tengo permisos para borrar mensajes.",
                    ephemeral=True
                )

            else:

                await ctx.send(
                    "❌ No tengo permisos para borrar mensajes.",
                    delete_after=5
                )


        except discord.HTTPException as error:

            print(
                f"❌ Error en /clear: {error}"
            )

            if ctx.interaction:

                await ctx.send(
                    "❌ Discord ha rechazado la operación.",
                    ephemeral=True
                )

            else:

                await ctx.send(
                    "❌ Discord ha rechazado la operación.",
                    delete_after=5
                )


    # ========================================================
    # ERRORES
    # ========================================================

    @clear.error
    async def clear_error(
        self,
        ctx,
        error
    ):

        if isinstance(
            error,
            commands.MissingPermissions
        ):

            mensaje = (
                "❌ Este comando es solo para "
                "**administradores**."
            )

        elif isinstance(
            error,
            commands.BotMissingPermissions
        ):

            mensaje = (
                "❌ Necesito el permiso "
                "**Gestionar mensajes**."
            )

        elif isinstance(
            error,
            commands.MissingRequiredArgument
        ):

            mensaje = (
                "❌ Debes indicar una cantidad.\n\n"
                "Ejemplo: `/clear 10`"
            )

        elif isinstance(
            error,
            commands.BadArgument
        ):

            mensaje = (
                "❌ La cantidad debe ser un número.\n\n"
                "Ejemplo: `/clear 10`"
            )

        else:

            print(
                f"❌ Error en /clear: {error}"
            )

            return


        # ====================================================
        # ERROR PRIVADO
        # ====================================================

        if ctx.interaction:

            await ctx.send(
                mensaje,
                ephemeral=True
            )

        else:

            await ctx.send(
                mensaje,
                delete_after=5
            )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    if bot.get_cog("Clear") is not None:

        print(
            "⚠️ Clear ya estaba cargado."
        )

        return

    await bot.add_cog(
        Clear(bot)
    )

    print(
        "✅ Clear.py cargado correctamente."
    )
