import discord
from discord.ext import tasks, commands
import os

# Configuración básica
TOKEN = os.getenv("DISCORD_TOKEN") 

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True  # <- CORRECCIÓN: Permite al bot ver e identificar los canales del servidor

bot = commands.Bot(command_prefix="!", intents=intents)

# Simulación de la base de datos de nc1.eu
datos_ligas = {
    "league-1": {
        "Mapa 01 - Dirt Stadium": [("Piloto_A", "1:12.345", "http://nc1.eu"), ("Piloto_B", "1:12.510", "http://nc1.eu"), ("Piloto_C", "1:12.890", "http://nc1.eu")],
        "Mapa 02 - Canyon Mud": [("Piloto_X", "0:58.200", "#"), ("Piloto_Y", "0:58.610", "#"), ("Piloto_Z", "0:59.001", "#")]
    },
    "league-2": {},
    "league-3": {}
}

mensajes_guardados = {}

@bot.event
async def on_ready():
    print(f"🤖 Bot conectado como {bot.user.name}")
    # Asegura que el bucle no intente arrancar antes de que el bot esté totalmente listo
    if not actualizar_tiempos.is_running():
        actualizar_tiempos.start()

@tasks.loop(minutes=5)
async def actualizar_tiempos():
    # Espera a que el bot esté bien conectado internamente para no leer datos vacíos
    await bot.wait_until_ready()
    
    for guild in bot.guilds:
        for liga, mapas in datos_ligas.items():
            canal = discord.utils.get(guild.text_channels, name=liga)
            if not canal: 
                continue 

            for nombre_mapa, podio in mapas.items():
                embed = discord.Embed(
                    title=f"📌 {nombre_mapa.upper()}", 
                    color=discord.Color.gold() if liga == "league-1" else discord.Color.blue()
                )
                
                medallas = ["🥇", "🥈", "🥉"]
                descripcion = ""
                
                for i, piloto in enumerate(podio):
                    nombre, tiempo, url_replay = piloto
                    link = f"[🏎️ Descargar Replay]({url_replay})" if url_replay != "#" else "*Sin replay*"
                    descripcion += f"{medallas[i]} **{nombre}** - `{tiempo}` | {link}\n"
                
                embed.description = descripcion if descripcion else "Nadie ha corrido aún en este mapa."
                embed.set_footer(text="Actualizado automáticamente desde nc1.eu")

                id_clave = f"{guild.id}_{liga}_{nombre_mapa}"
                if id_clave in mensajes_guardados:
                    try:
                        msg = await canal.fetch_message(mensajes_guardados[id_clave])
                        await msg.edit(embed=embed)
                    except:
                        msg = await canal.send(embed=embed)
                        mensajes_guardados[id_clave] = msg.id
                else:
                    msg = await canal.send(embed=embed)
                    mensajes_guardados[id_clave] = msg.id

bot.run(TOKEN)
