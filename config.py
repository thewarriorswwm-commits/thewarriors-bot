import os
from dotenv import load_dotenv


# ============================================================
# CARGAR .ENV
# ============================================================

load_dotenv()


# ============================================================
# TOKEN DEL BOT
# ============================================================

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError(
        "❌ No se ha encontrado DISCORD_TOKEN en el archivo .env"
    )


# ============================================================
# CANALES
# ============================================================

CANAL_BIENVENIDA = "bienvenida-🫂"
CANAL_GUERRAS = "guerras"
CANAL_UTILIDADES = "utilidades-🛠️"


# ============================================================
# ROLES
# ============================================================

ROL_MIEMBRO = "Miembro"
ROL_NORMAS = "Normas"


# ============================================================
# API / IA
# ============================================================

GROQ_URL = "https://api.groq.com/openai/v1"
MODEL = "llama-3.3-70b-versatile"


# ============================================================
# BÚSQUEDAS
# ============================================================

MAX_RESULTADOS_POR_BUSQUEDA = 6
MAX_RESULTADOS_TOTALES = 12
