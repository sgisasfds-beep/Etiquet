from pymongo import MongoClient
import re

# 1. Mapa de la tabla SGA (Traducciones oficiales)
mapa_frases_h = {
    # Peligros Físicos
    "H200": "Explosivo inestable",
    "H201": "Explosivo; peligro de explosión en masa",
    "H202": "Explosivo; grave peligro de proyección",
    "H203": "Explosivo; peligro de incendio, de onda expansiva o de proyección",
    "H204": "Peligro de incendio o de proyección",
    "H205": "Peligro de explosión en masa en caso de incendio",
    "H206": "Peligro de incendio, onda expansiva o proyección; mayor riesgo de explosión si se reduce el agente insensibilizante",
    "H207": "Peligro de incendio o proyección; mayor riesgo de explosión si se reduce el agente insensibilizante",
    "H208": "Peligro de incendio; mayor riesgo de explosión si se reduce el agente insensibilizante",
    "H220": "Gas extremadamente inflamable",
    "H221": "Gas inflamable",
    "H222": "Aerosol extremadamente inflamable",
    "H223": "Aerosol inflamable",
    "H224": "Líquido y vapores extremadamente inflamables",
    "H225": "Líquido y vapores muy inflamables",
    "H226": "Líquido y vapores inflamables",
    "H227": "Líquido combustible",
    "H228": "Sólido inflamable",
    "H229": "Contiene gas a presión: Puede reventar si se calienta",
    "H230": "Puede explotar incluso en ausencia de aire",
    "H231": "Puede explotar incluso en ausencia de aire, a presión y/o temperatura elevadas",
    "H232": "Puede inflamarse espontáneamente en contacto con el aire",
    "H240": "Puede explotar al calentarse",
    "H241": "Puede incendiarse o explotar al calentarse",
    "H242": "Puede incendiarse al calentarse",
    "H250": "Se inflama espontáneamente en contacto con el aire",
    "H251": "Se calienta espontáneamente; puede inflamarse",
    "H252": "Se calienta espontáneamente en grandes cantidades; puede inflamarse",
    "H260": "En contacto con el agua desprende gases inflamables que pueden inflamarse espontáneamente",
    "H261": "En contacto con el agua desprende gases inflamables",
    "H270": "Puede provocar o agravar un incendio; comburente",
    "H271": "Puede provocar un incendio o una explosión; muy comburente",
    "H272": "Puede agravar un incendio; comburente",
    "H280": "Contiene gas a presión; puede explotar si se calienta",
    "H281": "Contiene gas refrigerado; puede provocar quemaduras o lesiones criogénicas",
    "H290": "Puede ser corrosiva para los metales",

    # Peligros para la Salud
    "H300": "Mortal en caso de ingestión",
    "H301": "Tóxico en caso de ingestión",
    "H302": "Nocivo en caso de ingestión",
    "H303": "Puede ser nocivo en caso de ingestión",
    "H304": "Puede ser mortal en caso de ingestión y de penetración en las vías respiratorias",
    "H305": "Puede ser nocivo en caso de ingestión y de penetración en las vías respiratorias",
    "H310": "Mortal en contacto con la piel",
    "H311": "Tóxico en contacto con la piel",
    "H312": "Nocivo en contacto con la piel",
    "H313": "Puede ser nocivo en contacto con la piel",
    "H314": "Provoca graves quemaduras en la piel y lesiones oculares",
    "H315": "Provoca irritación cutánea",
    "H316": "Provoca una leve irritación cutánea",
    "H317": "Puede provocar una reacción cutánea alérgica",
    "H318": "Provoca lesiones oculares graves",
    "H319": "Provoca irritación ocular grave",
    "H320": "Provoca irritación ocular",
    "H330": "Mortal si se inhala",
    "H331": "Tóxico si se inhala",
    "H332": "Nocivo si se inhala",
    "H333": "Puede ser nocivo si se inhala",
    "H334": "Puede provocar síntomas de alergia o asma o dificultades respiratorias si se inhala",
    "H335": "Puede irritar las vías respiratorias",
    "H336": "Puede provocar somnolencia o vértigo",
    "H340": "Puede provocar defectos genéticos",
    "H341": "Susceptible de provocar defectos genéticos",
    "H350": "Puede provocar cáncer",
    "H351": "Susceptible de provocar cáncer",
    "H360": "Puede perjudicar la fertilidad o dañar al feto",
    "H361": "Susceptible de perjudicar la fertilidad o dañar al feto",
    "H362": "Puede ser nocivo para los lactantes",
    "H370": "Provoca daños en los órganos",
    "H371": "Puede provocar daños en los órganos",
    "H372": "Provoca daños en los órganos tras exposiciones prolongadas o repetidas",
    "H373": "Puede provocar daños en los órganos tras exposiciones prolongadas o repetidas",

    # Peligros para el Medio Ambiente
    "H400": "Muy tóxico para los organismos acuáticos",
    "H401": "Tóxico para los organismos acuáticos",
    "H402": "Nocivo para los organismos acuáticos",
    "H410": "Muy tóxico para los organismos acuáticos, con efectos nocivos duraderos",
    "H411": "Tóxico para los organismos acuáticos, con efectos nocivos duraderos",
    "H412": "Nocivo para los organismos acuáticos, con efectos nocivos duraderos",
    "H413": "Puede ser nocivo para los organismos acuáticos, con efectos nocivos duraderos",
    "H420": "Causa daños a la salud pública y el medio ambiente al destruir el ozono en la atmósfera superior"
}

def ejecutar_migracion_total():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["ReactivosDB"]
    coleccion = db["reactivos"]

    actualizados = 0
    no_modificados = []

    try:
        # Buscamos todos los documentos
        reactivos = list(coleccion.find({}))

        for doc in reactivos:
            frases_originales = doc.get("frases_h", [])
            nuevas_frases = []
            hubo_cambio_en_doc = False
            errores_en_doc = []

            # Verificación de tipo de dato
            if not isinstance(frases_originales, list):
                no_modificados.append({
                    "nombre": doc.get("nombre", "Sin nombre"),
                    "codigo_interno": doc.get("codigo", "S/C"),
                    "motivo": f"El campo frases_h no es una lista, es: {type(frases_originales).__name__}",
                    "contenido": frases_originales
                })
                continue

            if len(frases_originales) == 0:
                no_modificados.append({
                    "nombre": doc.get("nombre", "Sin nombre"),
                    "codigo_interno": doc.get("codigo", "S/C"),
                    "motivo": "La lista frases_h está vacía",
                    "contenido": []
                })
                continue

            for frase in frases_originales:
                # re.search busca el patrón H + 3 números en cualquier parte del texto
                match = re.search(r"(H\d{3})", str(frase), re.IGNORECASE)

                if match:
                    codigo = match.group(1).upper()
                    if codigo in mapa_frases_h:
                        nueva_descripcion = f"{codigo}: {mapa_frases_h[codigo]}"
                        nuevas_frases.append(nueva_descripcion)
                        hubo_cambio_en_doc = True
                    else:
                        nuevas_frases.append(frase)
                        errores_en_doc.append(f"Código {codigo} no existe en la tabla SGA proporcionada")
                else:
                    nuevas_frases.append(frase)
                    errores_en_doc.append(f"No se encontró un código H válido en el texto: '{frase}'")

            if hubo_cambio_en_doc:
                coleccion.update_one(
                    {"_id": doc["_id"]},
                    {"$set": {"frases_h": nuevas_frases}}
                )
                actualizados += 1
                print(f"✅ ACTUALIZADO: {doc.get('nombre')}")
            else:
                no_modificados.append({
                    "nombre": doc.get("nombre", "Sin nombre"),
                    "codigo_interno": doc.get("codigo", "S/C"),
                    "motivo": "No se realizaron cambios en ninguna frase",
                    "contenido_original": frases_originales,
                    "errores_detalle": errores_en_doc
                })

        # --- IMPRESIÓN DE RESULTADOS SIN LÍMITES ---
        print("\n" + "="*80)
        print("RESUMEN FINAL")
        print("="*80)
        print(f"Total procesados: {len(reactivos)}")
        print(f"Actualizados con éxito: {actualizados}")
        print(f"Sin cambios: {len(no_modificados)}")
        print("="*80)

        if len(no_modificados) > 0:
            print("\nLISTADO COMPLETO DE REGISTROS NO MODIFICADOS:")
            for idx, item in enumerate(no_modificados, 1):
                print(f"\n[{idx}] Reactivo: {item['nombre']} | Código: {item['codigo_interno']}")
                print(f"    Motivo: {item['motivo']}")

                if "contenido" in item:
                    print(f"    Valor actual: {item['contenido']}")

                if "contenido_original" in item:
                    print(f"    Frases actuales en DB: {item['contenido_original']}")

                if "errores_detalle" in item and item["errores_detalle"]:
                    print(f"    Alertas detectadas:")
                    for err in item["errores_detalle"]:
                        print(f"      - {err}")
            print("\n" + "="*80)
            print("FIN DEL LISTADO")

    except Exception as e:
        print(f"❌ ERROR CRÍTICO: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    ejecutar_migracion_total()
