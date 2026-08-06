import os
import asyncio
import discord

from discord.ext import commands
from openai import AsyncOpenAI
from ddgs import DDGS


# ============================================================
# CONFIGURACIÓN
# ============================================================

CANAL_IA = "ia-where-winds-meet-🤖"

GROQ_URL = "https://api.groq.com/openai/v1"

MODEL = "llama-3.3-70b-versatile"

MAX_RESULTADOS_POR_BUSQUEDA = 6
MAX_RESULTADOS_TOTALES = 12


# ============================================================
# BÚSQUEDA EN INTERNET
# ============================================================

async def buscar_internet(pregunta, categoria):

    def buscar():

        resultados = []
        urls = set()

        consultas = [
            f"Where Winds Meet {pregunta}",
            f"Where Winds Meet {categoria} {pregunta}",
            f"Where Winds Meet guide {pregunta}"
        ]

        try:

            with DDGS() as ddgs:

                for consulta in consultas:

                    print(f"🔎 Buscando: {consulta}")

                    try:

                        encontrados = ddgs.text(
                            consulta,
                            region="wt-wt",
                            safesearch="moderate",
                            timelimit=None,
                            max_results=MAX_RESULTADOS_POR_BUSQUEDA
                        )

                    except Exception as error:

                        print("⚠️ Error en una búsqueda:")
                        print(repr(error))
                        continue

                    if not encontrados:
                        continue

                    for resultado in encontrados:

                        titulo = str(
                            resultado.get("title", "")
                        ).strip()

                        url = str(
                            resultado.get("href", "")
                        ).strip()

                        descripcion = str(
                            resultado.get("body", "")
                        ).strip()

                        if not url:
                            continue

                        if url in urls:
                            continue

                        urls.add(url)

                        resultados.append({
                            "title": titulo,
                            "url": url,
                            "body": descripcion
                        })

                        if len(resultados) >= MAX_RESULTADOS_TOTALES:
                            break

                    if len(resultados) >= MAX_RESULTADOS_TOTALES:
                        break

        except Exception as error:

            print("❌ Error general buscando en Internet:")
            print(repr(error))

        return resultados

    return await asyncio.to_thread(buscar)


# ============================================================
# PREPARAR FUENTES
# ============================================================

def preparar_fuentes(resultados):

    if not resultados:

        return "NO SE ENCONTRARON RESULTADOS EN LA BÚSQUEDA WEB."

    fuentes = []

    for numero, resultado in enumerate(resultados, start=1):

        fuentes.append(
            f"""
FUENTE {numero}

Título:
{resultado["title"]}

URL:
{resultado["url"]}

Contenido:
{resultado["body"]}
"""
        )

    return "\n".join(fuentes)


# ============================================================
# MODAL DE PREGUNTA
# ============================================================

class PreguntaWWMModal(discord.ui.Modal):

    def __init__(
        self,
        categoria="Todo sobre Where Winds Meet"
    ):

        super().__init__(
            title="🤖 IA Where Winds Meet"
        )

        self.categoria = categoria

        self.pregunta = discord.ui.TextInput(
            label="¿Qué quieres preguntar?",
            placeholder=(
                "Escribe tu pregunta sobre "
                "Where Winds Meet..."
            ),
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=2000
        )

        self.add_item(self.pregunta)

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        print("==========================================")
        print("🤖 BOTÓN DE IA PULSADO")
        print("==========================================")

        try:

            await interaction.response.defer(
                ephemeral=True
            )

            print("✅ Discord ha recibido la interacción.")

        except Exception as error:

            print("❌ Error haciendo defer:")
            print(repr(error))
            return

        # ====================================================
        # GROQ
        # ====================================================

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:

            print("❌ GROQ_API_KEY NO ENCONTRADA.")

            await interaction.followup.send(
                "❌ La IA no está configurada correctamente.\n\n"
                "Falta **GROQ_API_KEY**.",
                ephemeral=True
            )

            return

        print("✅ GROQ_API_KEY encontrada.")

        # ====================================================
        # PREGUNTA
        # ====================================================

        pregunta = self.pregunta.value.strip()

        print(f"📝 Pregunta: {pregunta}")
        print(f"📂 Categoría: {self.categoria}")

        # ====================================================
        # BUSCAR INTERNET
        # ====================================================

        print("==========================================")
        print("🔎 BUSCANDO INFORMACIÓN EN INTERNET")
        print("==========================================")

        try:

            resultados = await buscar_internet(
                pregunta,
                self.categoria
            )

        except Exception as error:

            print("❌ Error buscando:")
            print(repr(error))

            resultados = []

        print(
            f"🌐 Resultados encontrados: {len(resultados)}"
        )

        for numero, resultado in enumerate(
            resultados,
            start=1
        ):

            print(f"\n🔎 FUENTE {numero}")
            print(f"Título: {resultado['title']}")
            print(f"URL: {resultado['url']}")
            print(
                f"Info: {resultado['body'][:300]}"
            )

        fuentes = preparar_fuentes(resultados)

        # ====================================================
        # CLIENTE GROQ
        # ====================================================

        cliente = AsyncOpenAI(
            api_key=api_key,
            base_url=GROQ_URL,
            timeout=45.0
        )

        # ====================================================
        # INSTRUCCIONES
        # ====================================================

        instrucciones = f"""
Eres una IA especializada en el videojuego
Where Winds Meet para el servidor de Discord
Thewarriors.

Responde SIEMPRE en español.

Categoría:
{self.categoria}

Pregunta del usuario:
{pregunta}

============================================================
INFORMACIÓN ENCONTRADA EN INTERNET
============================================================

{fuentes}

============================================================
REGLAS OBLIGATORIAS
============================================================

1. CONTESTA LA PREGUNTA EXACTA DEL USUARIO.

2. Analiza primero los resultados encontrados
   en Internet.

3. Si los resultados contienen la respuesta,
   UTILIZA ESA INFORMACIÓN.

4. No respondas simplemente que no tienes
   información si la búsqueda sí encontró
   información útil.

5. NO INVENTES información.

6. NO INVENTES builds.

7. NO INVENTES armas.

8. NO INVENTES habilidades.

9. NO INVENTES estadísticas.

10. NO INVENTES ubicaciones.

11. NO INVENTES NPC.

12. NO INVENTES misiones.

13. NO INVENTES eventos.

14. NO INVENTES actualizaciones.

15. Si una fuente proporciona una build,
    explica exactamente lo que aparece
    en esa fuente.

16. Si preguntan por la mejor build,
    analiza primero las fuentes encontradas.

17. Si existen varias opciones,
    compáralas y explica cuál parece
    mejor según la información encontrada.

18. No digas automáticamente que todo
    depende del estilo del jugador.

19. Si las fuentes no permiten confirmar
    un dato, dilo claramente.

20. Si las fuentes se contradicen,
    indícalo.

21. No inventes fuentes.

22. No inventes URLs.

23. Responde directamente y de forma clara.

24. Si has utilizado resultados de Internet,
    añade al final:

🔎 Fuentes:
- Título — URL

25. Utiliza únicamente las URLs que aparecen
    en los resultados proporcionados.
"""

        # ====================================================
        # CONSULTAR GROQ
        # ====================================================

        try:

            print(
                "🧠 Enviando pregunta y búsqueda web a Groq..."
            )

            respuesta = await cliente.chat.completions.create(

                model=MODEL,

                messages=[
                    {
                        "role": "system",
                        "content": instrucciones
                    },
                    {
                        "role": "user",
                        "content": pregunta
                    }
                ],

                temperature=0.2,

                max_tokens=1500
            )

            print("✅ Groq ha respondido.")

            if (
                not respuesta.choices
                or not respuesta.choices[0].message.content
            ):

                texto = (
                    "❌ La IA no ha devuelto "
                    "ninguna respuesta."
                )

            else:

                texto = (
                    respuesta
                    .choices[0]
                    .message
                    .content
                    .strip()
                )

            # =================================================
            # DIVIDIR RESPUESTA
            # =================================================

            partes = [
                texto[i:i + 1900]
                for i in range(
                    0,
                    len(texto),
                    1900
                )
            ]

            # =================================================
            # ENVIAR RESPUESTA
            # =================================================

            for parte in partes:

                await interaction.followup.send(
                    parte,
                    ephemeral=True
                )

            print("✅ Respuesta enviada a Discord.")

        except asyncio.TimeoutError:

            print("❌ GROQ TARDÓ DEMASIADO.")

            await interaction.followup.send(
                "❌ La IA tardó demasiado en responder.",
                ephemeral=True
            )

        except Exception as error:

            print("==========================================")
            print("❌ ERROR EN LA IA")
            print(repr(error))
            print("==========================================")

            try:

                await interaction.followup.send(
                    "❌ No se ha podido consultar la IA.\n\n"
                    "Revisa la consola del bot.",
                    ephemeral=True
                )

            except Exception as error2:

                print("❌ Error enviando el mensaje:")
                print(repr(error2))


# ============================================================
# PANEL
# ============================================================

class WhereWindsMeetView(discord.ui.View):

    def __init__(self):

        super().__init__(
            timeout=None
        )

    async def abrir(
        self,
        interaction: discord.Interaction,
        categoria: str
    ):

        await interaction.response.send_modal(
            PreguntaWWMModal(categoria)
        )

    @discord.ui.button(
        label="Preguntar a la IA",
        emoji="🤖",
        style=discord.ButtonStyle.primary,
        custom_id="wwm_general",
        row=0
    )
    async def general(
        self,
        interaction,
        button
    ):

        await self.abrir(
            interaction,
            "Todo sobre Where Winds Meet"
        )

    @discord.ui.button(
        label="Misiones y guías",
        emoji="🗺️",
        style=discord.ButtonStyle.secondary,
        custom_id="wwm_misiones",
        row=0
    )
    async def misiones(
        self,
        interaction,
        button
    ):

        await self.abrir(
            interaction,
            "Misiones y guías"
        )

    @discord.ui.button(
        label="Builds y habilidades",
        emoji="⚔️",
        style=discord.ButtonStyle.secondary,
        custom_id="wwm_builds",
        row=0
    )
    async def builds(
        self,
        interaction,
        button
    ):

        await self.abrir(
            interaction,
            "Builds y habilidades"
        )

    @discord.ui.button(
        label="Objetos y ubicaciones",
        emoji="🎒",
        style=discord.ButtonStyle.secondary,
        custom_id="wwm_objetos",
        row=1
    )
    async def objetos(
        self,
        interaction,
        button
    ):

        await self.abrir(
            interaction,
            "Objetos, materiales y ubicaciones"
        )

    @discord.ui.button(
        label="Jefes y enemigos",
        emoji="👹",
        style=discord.ButtonStyle.secondary,
        custom_id="wwm_jefes",
        row=1
    )
    async def jefes(
        self,
        interaction,
        button
    ):

        await self.abrir(
            interaction,
            "Jefes y enemigos"
        )

    @discord.ui.button(
        label="Artes marciales",
        emoji="🥋",
        style=discord.ButtonStyle.secondary,
        custom_id="wwm_artes",
        row=1
    )
    async def artes(
        self,
        interaction,
        button
    ):

        await self.abrir(
            interaction,
            "Artes marciales y estilos de combate"
        )

    @discord.ui.button(
        label="Equipamiento",
        emoji="🛡️",
        style=discord.ButtonStyle.secondary,
        custom_id="wwm_equipo",
        row=2
    )
    async def equipo(
        self,
        interaction,
        button
    ):

        await self.abrir(
            interaction,
            "Equipamiento, armas y progresión"
        )

    @discord.ui.button(
        label="Novedades",
        emoji="🆕",
        style=discord.ButtonStyle.success,
        custom_id="wwm_novedades",
        row=2
    )
    async def novedades(
        self,
        interaction,
        button
    ):

        await self.abrir(
            interaction,
            "Novedades, actualizaciones y cambios recientes"
        )


# ============================================================
# COG
# ============================================================

class WhereWindsMeet(commands.Cog):

    def __init__(self, bot):

        self.bot = bot
        self.iniciado = False

    # ========================================================
    # INICIO AUTOMÁTICO
    # ========================================================

    @commands.Cog.listener()
    async def on_ready(self):

        if self.iniciado:
            return

        self.iniciado = True

        print(
            "🤖 Iniciando IA Where Winds Meet..."
        )

        for guild in self.bot.guilds:

            print(
                f"🔎 Comprobando servidor: {guild.name}"
            )

            # =================================================
            # BUSCAR CANAL
            # =================================================

            canal = discord.utils.get(
                guild.text_channels,
                name=CANAL_IA
            )

            # =================================================
            # CREAR CANAL
            # =================================================

            if canal is None:

                print(
                    f"⚠️ #{CANAL_IA} no existe."
                )

                try:

                    canal = await guild.create_text_channel(
                        CANAL_IA,
                        topic=(
                            "🤖 IA Where Winds Meet "
                            "• Thewarriors"
                        ),
                        reason=(
                            "Creación automática "
                            "del canal de IA"
                        )
                    )

                    print(
                        f"✅ Canal #{CANAL_IA} creado."
                    )

                except Exception as error:

                    print(
                        "❌ No se pudo crear el canal:"
                    )

                    print(
                        repr(error)
                    )

                    continue

            else:

                print(
                    f"✅ Canal #{CANAL_IA} encontrado."
                )

            # =================================================
            # BUSCAR PANEL
            # =================================================

            panel = None

            try:

                async for mensaje in canal.history(
                    limit=100
                ):

                    if mensaje.author != self.bot.user:
                        continue

                    if not mensaje.embeds:
                        continue

                    if (
                        mensaje.embeds[0].title
                        == "🤖 IA — WHERE WINDS MEET"
                    ):

                        panel = mensaje
                        break

            except Exception as error:

                print(
                    "❌ Error buscando panel:"
                )

                print(
                    repr(error)
                )

            # =================================================
            # PANEL YA EXISTE
            # =================================================

            if panel:

                print(
                    "✅ El panel IA ya existe."
                )

                continue

            # =================================================
            # EMBED
            # =================================================

            embed = discord.Embed(

                title=(
                    "🤖 IA — WHERE WINDS MEET"
                ),

                description=(

                    "### 🛡️ Asistente de Where Winds Meet\n\n"

                    "¿Necesitas ayuda con el juego?\n\n"

                    "La IA puede ayudarte con "
                    "**misiones, builds, habilidades, "
                    "objetos, ubicaciones, jefes, "
                    "artes marciales, equipamiento "
                    "y mucho más.**\n\n"

                    "👇 **Selecciona una categoría "
                    "o pregunta directamente.**\n\n"

                    "🔒 **Las respuestas son privadas.**\n"
                    "Solo tú podrás ver tu conversación "
                    "con la IA."
                ),

                color=discord.Color.blue()
            )

            embed.add_field(
                name="🤖 Pregunta libre",
                value="Pregunta cualquier cosa",
                inline=False
            )

            embed.add_field(
                name="🗺️ Misiones y guías",
                value="Ayuda con misiones",
                inline=True
            )

            embed.add_field(
                name="⚔️ Builds y habilidades",
                value="Builds y combate",
                inline=True
            )

            embed.add_field(
                name="🎒 Objetos y ubicaciones",
                value="Objetos y materiales",
                inline=True
            )

            embed.add_field(
                name="👹 Jefes y enemigos",
                value="Jefes y enemigos",
                inline=True
            )

            embed.add_field(
                name="🥋 Artes marciales",
                value="Estilos de combate",
                inline=True
            )

            embed.add_field(
                name="🛡️ Equipamiento",
                value="Armas y progresión",
                inline=True
            )

            embed.add_field(
                name="🆕 Novedades",
                value="Actualizaciones",
                inline=True
            )

            embed.set_footer(
                text=(
                    "Thewarriors • "
                    "Where Winds Meet IA"
                )
            )

            # =================================================
            # ENVIAR PANEL
            # =================================================

            try:

                await canal.send(
                    embed=embed,
                    view=WhereWindsMeetView()
                )

                print(
                    "✅ Panel IA creado correctamente."
                )

            except Exception as error:

                print(
                    "❌ Error creando el panel:"
                )

                print(
                    repr(error)
                )

        print(
            "=========================================="
        )

        print(
            "🤖 IA WHERE WINDS MEET INICIADA"
        )

        print(
            "=========================================="
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        WhereWindsMeet(bot)
    )

    bot.add_view(
        WhereWindsMeetView()
    )

    print(
        "✅ WhereWindsMeet cargado."
    )
