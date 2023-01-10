#!/bin/python3
# coding: utf-8

# Uso: python3 get_offer.py *clave_de_materia1_* *clave_de_materia_2* ...
# Todos los demás datos vienen hardcodeados

# pip3 install requests beautifulsoup4
import argparse
import xml.etree.ElementTree as ET

from constantes import *
from CatalogoMaterias import CatalogoMaterias

def obtenerPlanes():
    rutaPlanesXml = os.path.join(CARPETA_DATOS, "planes.xml")
    return ET.parse(rutaPlanesXml).findall("plan")


def procesarArgumentosConsola():
    letras_centros = ['3']
    letras_centros.extend([chr(x) for x in range(65, 91)])
    parser = argparse.ArgumentParser()
    parser.add_argument("claves", help="La(s) clave(s) de la(s) materia(s)", nargs="*")
    parser.add_argument("-c", "--centro",
                        help="La letra identificadora del centro universitario a añadir",
                        choices=letras_centros,
                        default=CENTRO_DEF)
    parser.add_argument("-2", "--ciclo",
                        help="El ciclo escolar a buscar. Debe de estar en formato SIIAU (202210)",
                        default=CICLO_ACTUAL)
    parser.add_argument("-p", "--plan",
                        help="El plan de estudios a buscar. Ej. ICOM, LQUI...",
                        default=PLAN_DEF)
    
    return parser.parse_args()


def main():
    args = procesarArgumentosConsola()
    materias = []

    # Si hay claves, iteramos y obtenemos la oferta de cada una
    if args.claves:
        catalogo = CatalogoMaterias(args.plan,
                                    prevenirAutoActualizacion=True)
        for clave in args.claves:
            if len(clave) == 5 and clave.isalnum():
                materias = catalogo.consultarSiiau(args.ciclo,
                                                   args.centro,
                                                   clave)
            else:
                print(f"Error: La clave '{clave}' es inválida. Saltando...")

        for materia in materias:
            catalogo.actualizar(materia)

    # Sino, por defecto actualizamos el catálogo de planes completo
    else:
        catalogo = CatalogoMaterias(PLAN_DEF,
                                    prevenirAutoActualizacion=True)
        planes = obtenerPlanes()
        for planTag in planes:
            catalogo.actualizarPlanSeleccionado(planTag.attrib["id"])
            print(f"Actualizando {catalogo.idPlan}...")
            materias = catalogo.consultarSiiau(CICLO_ACTUAL, CENTRO_DEF)
            catalogo.actualizarTodo(materias)

    print("Actualización finalizada")


if __name__ == "__main__":
    main()
