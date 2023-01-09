#!/bin/python3
# coding: utf-8
#
# Uso: python3 get_offer.py *clave_de_materia1_* *clave_de_materia_2* ...
# Todos los demás datos vienen hardcodeados

# pip3 install requests beautifulsoup4
import argparse
import Horario
import Materia
from gen_cat import generarCatalogoMaterias
import requests
import bs4

# Datos necesarios para obtener la oferta
SERVIDOR_SIIAU = 'http://consulta.siiau.udg.mx'
APP_SIIAU = f'{SERVIDOR_SIIAU}/wco/sspseca.consulta_oferta'
CICLO_ACTUAL = "202220"  # Calendario 22B
CENTRO_DEF = "D"  # CUCEI
PLAN_DEF = "ICOM"  # Computación, técnicamente no es necesario pero de todos modos lo agrego
# Número de clases a mostrar, ponemos un valor exagerado para asegurarnos que nos muestre todos
CANT_RESULT_DEF = 10000  # Índice clases


def extraerDatosFila(nodo: bs4.Tag):
    datos = []
    for celda in nodo.find_all("td", recursive=False):
        for element in celda.children:
            if element.name == "table":
                filas = extraerDatosTabla(element)
                datos.append(filas)
            else:
                if not element.text:
                    continue
                datos.append(element.text.strip())

    return datos


def extraerDatosTabla(tabla: bs4.PageElement, saltarFilasInvalidas: bool = False, cantCeldasEsperadas: int = 0):
    tabla = tabla.find("tbody") if tabla.find("tbody") else tabla
    datosTabla = []
    for node in tabla.find_all("tr", recursive=False):
        if saltarFilasInvalidas:
            if len(node.find_all("td", recursive=False)) < cantCeldasEsperadas:
                continue
        fila = extraerDatosFila(node)
        if fila:
            datosTabla.append(fila)

    return datosTabla


def consultarSiiau(ciclo: str = CICLO_ACTUAL,
                   centro: str = CENTRO_DEF,
                   carrera: str = PLAN_DEF,
                   materia: str = "",
                   cantResultados: int = CANT_RESULT_DEF,
                   indiceInicio: int = 0):
    """
    Realiza una consulta de oferta académica al SIIAU y retorna una lista con los resultados
    - return: Una lista con objetos materia, convertibles a diccionarios
    - rtype: Materia[]
    """
    materias_obtenidas = []
    datos_post = {
        'ciclop': ciclo,
        'cup': centro,
        'majrp': carrera,
        'crsep': materia,
        'mostrarp': cantResultados,
        'p_start': indiceInicio,
    }
    if indiceInicio < 1:
        datos_post.pop("p_start")
    try:
        response = requests.post(APP_SIIAU, data=datos_post)
    except (ConnectionError, requests.exceptions.ConnectionError):
        print("Ocurió un error conectando con SIIAU.")
        respuesta = ""
    else:
        respuesta = response.text

    if respuesta:
        soup = bs4.BeautifulSoup(respuesta, "html5lib")
        table = soup.body.table
        datos = extraerDatosTabla(table)

        for entrada in datos:
            horarios = []

            for fila in entrada[8]:
                horario = Horario(centro, fila[0], fila[1], fila[2],
                                  fila[3], fila[4], fila[5])
                horarios.append(horario)

            profesor = entrada[10][0][1] if entrada[10] else ""

            materia_obj = Materia(centro, int(entrada[0]), entrada[1],
                                  entrada[2], entrada[3], int(entrada[4]),
                                  int(entrada[5]), int(entrada[6]),
                                  horarios, profesor)
            materias_obtenidas.append(materia_obj)

    return materias_obtenidas


def main():
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
    args = parser.parse_args()

    materias = []

    # Si hay claves, iteramos y obtenemos la oferta de cada una
    if args.claves:
        for clave in args.claves:
            if len(clave) == 5 and clave.isascii() and clave.isalnum():
                materias.extend(consultarSiiau(args.ciclo,
                                               args.centro,
                                               args.plan,
                                               clave))
            else:
                print(f"Error: La clave '{clave}' es inválida. Saltando...")

    # Sino, por defecto actualizamos el catálogo completo de ICOM
    else:
        materias.extend(consultarSiiau(args.ciclo, args.centro, args.plan))

    generarCatalogoMaterias(materias)

    print("Actualización finalizada")


if __name__ == "__main__":
    main()
