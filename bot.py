import discord
from discord.ext import tasks, commands
import os

# Configuración básica
TOKEN = os.getenv("DISCORD_TOKEN") # Se protege la llave en la nube

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Simulación de la base de datos de nc1.eu (Aquí conectará tu plugin chivato)
# Estructura: "Liga": {"Mapa": [🥇, 🥈, 🥉]}
datos_ligas = {
    "liga_1": {
        "Mapa 01 - Dirt Stadium": [("Piloto_A", "1:12.345", "http://nc1.eu"), ("Piloto_B", "1:12.510", "http://nc1.eu"), ("Piloto_C", "1:12.890", "http://nc1.eu")],
        "Mapa 02 - Canyon Mud": [("Piloto_X", "0:58.200", "#"), ("Piloto_Y", "0:58.610", "#"), ("Piloto_Z", "0:59.001", "#")]
    },
    "liga_2": {},
    "liga_3": {}
}

# Diccionario para recordar qué mensaje corresponde a cada mapa y no duplicar
mensajes_guardados = {}

@bot.event
async def on_ready():
    print(f"🤖 Bot conectado como {bot.user.name}")
    actualizar_tiempos.start() # Inicia el bucle automático

@tasks.loop(minutes=5) # Revisa nc1.eu y actualiza Discord cada 5 minutos
async def actualizar_tiempos():
    # NOTA: Aquí el script leerá los archivos reales de nc1.eu en el futuro
    
    # IDs de tus canales de Discord (Los cambiaremos por los tuyos reales)
    canales_dict = {
        "liga_1": int(os.getenv("CANAL_LIGA_1", 0)),
        "liga_2": int(os.getenv("CANAL_LIGA_2", 0)),
        "liga_3": int(os.getenv("CANAL_LIGA_3", 0))
    }

    for liga, mapas in datos_ligas.items():
        id_canal = canales_dict.get(liga)
        if not id_canal: continue
        
        canal = bot.get_channel(id_canal)
        if not canal: continue

        for nombre_mapa, podio in mapas.items():
            # Creamos el diseño visual limpio (Embed)
            embed = discord.Embed(
                title==f"📌 {nombre_mapa.upper()}", 
                color=discord.Color.gold() if liga == "liga_1" else discord.Color.blue()
            )
            
            medallas = ["🥇", "🥈", "🥉"]
            descripcion = ""
            
            for i, piloto in enumerate(podio):
                nombre, tiempo, url_replay = piloto
                link = f"[🏎️ Descargar Replay]({url_replay})" if url_replay != "#" else "*Sin replay*"
                descripcion += f"{medallas[i]} **{nombre}** - `{tiempo}` | {link}\n"
            
            embed.description = descripcion if descripcion else "Nadie ha corrido aún en este mapa."
            embed.set_footer(text="Actualizado automáticamente desde nc1.eu")

            # Si ya publicamos este mapa antes, editamos el mensaje anterior para no inundar el canal
            id_clave = f"{liga}_{nombre_mapa}"
            if id_clave in mensajes_guardados:
                try:
                    msg = await canal.fetch_message(mensajes_guardados[id_clave])
                    await msg.edit(embed=embed)
                except:
                    # Si el mensaje fue borrado por error, lo recrea
                    msg = await canal.send(embed=embed)
                    mensajes_guardados[id_clave] = msg.id
            else:
                msg = await canal.send(embed=embed)
                mensajes_guardados[id_clave] = msg.id

bot.run(TOKEN)
