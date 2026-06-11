import nextcord
from nextcord.ext import tasks, commands
from aiohttp import web
import os
import asyncio

# 1. Configuración de Discord (Usando Nextcord)
TOKEN = os.getenv("DISCORD_TOKEN")
intents = nextcord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)
mensajes_guardados = {}

@bot.event
async def on_ready():
    print(f"🤖 Bot de la Liga conectado y listo como {bot.user.name}")

# 2. Servidor Web Integrado para recibir alertas de UASECO
async def recibir_record(request):
    try:
        data = await request.json()
        liga = data.get("liga")          
        mapa = data.get("mapa")          
        podio = data.get("podio", [])    
        
        bot.loop.create_task(publicar_tiempos_discord(liga, mapa, podio))
        return web.json_response({"status": "success", "message": "Datos recibidos"})
    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)}, status=400)

async def publicar_tiempos_discord(liga, nombre_mapa, podio):
    await bot.wait_until_ready()
    
    for guild in bot.guilds:
        canal = nextcord.utils.get(guild.text_channels, name=liga)
        if not canal: 
            continue

        embed = nextcord.Embed(
            title=f"📌 {nombre_mapa.upper()}", 
            color=nextcord.Color.gold() if liga == "league-1" else nextcord.Color.blue()
        )
        
        medallas = ["🥇", "🥈", "🥉"]
        descripcion = ""
        
        for i, piloto in enumerate(podio):
            if i >= len(medallas): break
            nombre = piloto
            tiempo = piloto
            url_replay = piloto if len(piloto) > 2 else "#"
            
            link = f"[🏎️ Descargar Replay]({url_replay})" if url_replay != "#" else "*Sin replay*"
            descripcion += f"{medallas[i]} **{nombre}** - `{tiempo}` | {link}\n"
        
        embed.description = descripcion if descripcion else "Nadie ha corrido aún en este mapa."
        embed.set_footer(text="Actualizado en tiempo real desde nc1.eu")

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

# 3. Arrancar Servidor API y Bot en paralelo
async def main():
    app = web.Application()
    app.router.add_post('/nuevo-record', recibir_record)
    
    puerto = int(os.getenv("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', puerto)
    
    await asyncio.gather(
        site.start(),
        bot.start(TOKEN)
    )

if __name__ == "__main__":
    asyncio.run(main())
