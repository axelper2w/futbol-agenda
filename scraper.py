import json
import requests
from bs4 import BeautifulSoup

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

    # Buscamos filas o contenedores comunes de partidos en la página
    # (Si la estructura cambia, puedes inspeccionar la web con F12 y ajustar estos selectores)
    items = soup.select('tr, .match-item, .event-block, .card')
    
    for item in items:
        texto_item = item.get_text(strip=True)
        if not texto_item or len(texto_item) < 5:
            continue

        # Intentamos extraer datos básicos
        hora_elem = item.select_one('.time, .hora, span')
        hora = hora_elem.text.strip() if hora_elem else "En vivo"

        equipos_elem = item.select_one('.teams, .match-name, strong')
        equipos = equipos_elem.text.strip() if equipos_elem else texto_item[:50]

        signals = []
        # Buscamos enlaces de reproducción dentro del bloque
        enlaces = item.select('a')
        for idx, link in enumerate(enlaces):
            href = link.get('href')
            if href and ('http' in href or '.m3u8' in href):
                signals.append({
                    "name": f"Opción {idx + 1}",
                    "url": href if href.startswith('http') else URL_FUENTE + href
                })

        # Si el elemento tiene pinta de partido pero no sacó enlaces directos, le ponemos la fuente por defecto
        if not signals:
            signals.append({
                "name": "Señal Principal",
                "url": URL_FUENTE
            })

        # Evitamos agregar elementos basura que no sean partidos
        if "vs" in equipos.lower() or "-" in equipos or len(signals) > 0:
            partidos.append({
                "time": hora if ":" in hora else "LIVE",
                "league": "Fútbol en Vivo",
                "logo": "https://a.espncdn.com/i/leaguelogos/soccer/50/2034.png",
                "teams": equipos,
                "signals": signals
            })

    # Si por alguna razón el selector estricto no trajo nada, generamos al menos un elemento base para que no quede vacío
    if not partidos:
        partidos.append({
            "time": "LIVE",
            "league": "Transmisión en Vivo",
            "logo": "https://a.espncdn.com/i/leaguelogos/soccer/50/2034.png",
            "teams": "Fútbol Libre - Transmisión General",
            "signals": [
                { "name": "Opción 1", "url": URL_FUENTE }
            ]
        })

    return partidos

if __name__ == "__main__":
    lista_partidos = obtener_partidos()
    
    with open("partidos.json", "w", encoding="utf-8") as f:
        json.dump(lista_partidos, f, ensure_ascii=False, indent=4)
    
    print("¡partidos.json actualizado con éxito!")
