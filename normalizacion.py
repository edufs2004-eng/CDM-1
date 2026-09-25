import unicodedata

def normalizar_texto(valor):
    valor = str(valor).strip().lower()
    valor = unicodedata.normalize("NFKD", valor)
    return "".join(c for c in valor if not unicodedata.combining(c))

ETIQUETAS_CANONICAS = {
    "acuatico": "Acuático",
    "hibrido": "Híbrido",
    "terrestre": "Terrestre",
    "volador": "Volador",
    "ataque a distancia": "Ataque a distancia",
    "titanico": "Titánico",
    "gigante": "Gigante",
    "mecanico": "Mecánico",
    "barca": "Barca",
}

def normalizar_etiqueta(etiqueta):
    clave = normalizar_texto(etiqueta)
    return ETIQUETAS_CANONICAS.get(clave, str(etiqueta).strip())

def normalizar_etiquetas(etiquetas):
    if not etiquetas:
        return []
    return [normalizar_etiqueta(e) for e in etiquetas if str(e).strip()]

def normalizar_terreno(terreno):
    clave = normalizar_texto(terreno)
    equivalencias = {
        "tierra": "Tierra",
        "agua": "Agua",
        "agua profunda": "Agua profunda",
        "hibrido": "Híbrido",
        "mar": "Agua",
    }
    return equivalencias.get(clave, str(terreno).strip())