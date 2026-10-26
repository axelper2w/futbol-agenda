import json
import requests
from bs4 import BeautifulSoup

# 1. Cambia esta URL por la página real de donde quieres extraer la agenda
URL_FUENTE = "https://futbolvivo.tv/" 

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def obtener_partidos():
    response = requests.get(URL_FUENTE, headers=headers)
    if response.status_code != 200:
        print("Error al acceder a la fuente")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    partidos = []

    # 2. Ajusta estos selectores (.match-item, .time, etc.) según el diseño HTML de la web que elijas
    items = soup.select('.match-item')
    
    for item in items:
        hora = item.select_one('.time').text.strip() if item.select_one('.time') else "15:00"
        liga = item.select_one('.league').text.strip() if item.select_one('.league') else "Fútbol En Vivo"
        equipos = item.select_one('.teams').text.strip() if item.select_one('.teams') else "Partido"
        
        signals = []
        enlaces_opciones = item.select('a.embed-link')
        for idx, link in enumerate(enlaces_opciones):
            url_embed = link.get('href')
            signals.append({
                "name": f"Opción {idx + 1}",
                "url": url_embed
            })

        if signals:
            partidos.append({
                "time": hora,
                "league": liga,
                "logo": "https://a.espncdn.com/i/leaguelogos/soccer/50/2034.png",
                "teams": equipos,
                "signals": signals
            })

    return partidos

if __name__ == "__main__":
    lista_partidos = obtener_partidos()
    
    # Genera el archivo que leerá tu Blogger
    with open("partidos.json", "w", encoding="utf-8") as f:
        json.dump(lista_partidos, f, ensure_ascii=False, indent=4)
    
    print("¡partidos.json actualizado con éxito!")
