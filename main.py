import os
import asyncio

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

# ============================================================
# CARGAR .ENV
# ============================================================

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError(
        "❌ No se ha encontrado DISCORD_TOKEN."
    )

# ============================================================
# INTENTS
# ============================================================

intents = discord.Intents.default()

intents.presences = True
intents.members = True
intents.message_content = True

# ============================================================
# BOT
# ============================================================

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# ============================================================
# COGS
# ============================================================

COGS = [
    "cogs.Automod",
    "cogs.Bienvenida",
    "cogs.clear",
    "cogs.Eventos",
    "cogs.Guerras",
    "cogs.Logs",
    "cogs.Moderacion",
    "cogs.Tickets",
    "cogs.Utilidades",
    "cogs.WhereWindsMeet",
]

# ============================================================
# CARGAR COGS
# ============================================================

async def cargar_cogs():

    for cog in COGS:

        try:

            await bot.load_extension(cog)

            print(
                f"✅ COG CARGADO: {cog}"
            )

        except Exception as error:

            print(
                f"❌ ERROR EN {cog}: {error}"
            )

# ============================================================
# BOT LISTO
# ============================================================

@bot.event
async def on_ready():

    print("==========================================")
    print(f"🤖 BOT CONECTADO: {bot.user}")
    print(f"🆔 ID: {bot.user.id}")
    print("==========================================")

    try:

        synced = await bot.tree.sync()

        print(
            f"✅ COMANDOS SLASH SINCRONIZADOS: "
            f"{len(synced)}"
        )

        print("📋 COMANDOS DISPONIBLES:")

        for comando in synced:

            print(
                f"   /{comando.name}"
            )

        print("==========================================")

    except Exception as error:

        print(
            f"❌ ERROR AL SINCRONIZAR: {error}"
        )

# ============================================================
# ERROR GLOBAL DE COMANDOS PREFIX
# ============================================================

@bot.event
async def on_command_error(ctx, error):

    if isinstance(
        error,
        commands.CommandNotFound
    ):
        return

    if isinstance(
        error,
        commands.MissingPermissions
    ):

        await ctx.send(
            "❌ No tienes permisos para utilizar este comando.",
            delete_after=5
        )

        return

    if isinstance(
        error,
        commands.BotMissingPermissions
    ):

        await ctx.send(
            "❌ Al bot le faltan permisos.",
            delete_after=5
        )

        return

    print(
        f"❌ ERROR DE COMANDO: {error}"
    )

# ============================================================
# ERROR GLOBAL DE SLASH COMMANDS
# ============================================================

@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction,
    error
):

    if isinstance(
        error,
        app_commands.MissingPermissions
    ):

        if interaction.response.is_done():

            await interaction.followup.send(
                "❌ No tienes permisos para utilizar este comando.",
                ephemeral=True
            )

        else:

            await interaction.response.send_message(
                "❌ No tienes permisos para utilizar este comando.",
                ephemeral=True
            )

        return

    print(
        f"❌ ERROR SLASH COMMAND: {error}"
    )

# ============================================================
# INICIAR BOT
# ============================================================

async def main():

    await cargar_cogs()

    print(
        "🚀 Iniciando bot..."
    )

    await bot.start(
        TOKEN
    )

# ============================================================
# EJECUTAR
# ============================================================

if __name__ == "__main__":

    try:

        asyncio.run(
            main()
        )

    except KeyboardInterrupt:

        print(
            "🛑 Bot detenido."
        )

