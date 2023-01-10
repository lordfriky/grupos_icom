#!/bin/python3
# coding: utf-8
# pip3 install bs4 html5lib

import argparse
import os
import re

from constantes import *

from gen_web import generarPagina
from CatalogoMaterias import CatalogoMaterias


def verificarArgumentos():
    parser = argparse.ArgumentParser()
    parser.add_argument("clave", help="La clave de la materia")
    parser.add_argument("nrc", help="El NRC del grupo")
    parser.add_argument("link", help="El enlace de invitación de WhatsApp")

    if os.environ.get("ISSUE_BODY"):
        cuerpoIssue = os.environ.get("ISSUE_BODY")
        pattern = "(?ism)### Enlace de invitación\n\n(.+)\n\n### Clave de la materia\n\n(\w+)\n\n### NRC del curso\n\n(\d+)"
        matches = re.findall(pattern, cuerpoIssue, re.DOTALL)
        if matches:
            matches, = matches
            link, clave, nrc = matches
        else:
            print('Los datos del Issue no tienen el formato esperado. Verificar')
            exit(1)

    else:
        args = parser.parse_args()
        clave, nrc, link = args.clave, args.nrc, args.link

    if not os.environ.get("GIT_USER"):
        print("La variable de entorno 'GIT_USER' no está establecida. Se predetermina a lordfriky")
        os.environ["GIT_USER"] = "lordfriky"

    validaClaves = lambda clave, tam: len(
        clave) == tam and clave.isascii() and clave.isalnum()

    if not validaClaves(clave, 5):
        print(f'Error: La clave "{clave}" es inválida.')
        exit(1)

    if not validaClaves(nrc, 6):
        print(f'Error: El NRC "{nrc}" es inválido.')
        exit(1)

    # Limpiamos por si las instrucciones no fueron claras
    link = link.strip("<>")

    # Validamos que sea un link de WhatsApp
    if re.match(r"^https://(?:www\.)?chat\.whatsapp\.com/[\w]+", link) is None:
        print('Error: El link {} es inválido. Verifica que el link sea de WhatsApp y que comience con HTTPS y no HTTP'.format(link))
        exit(1)

    return clave, int(nrc), link


def agregarEnlaceAMaterias(clave: str, nrc: str, link: str):
    catalogo = CatalogoMaterias(PLAN_DEF)
    materias = catalogo.obtenerTodo()
    materia = None

    if not materias:
        exit(1)

    try:
        if materias.get(clave, {}):
            materia = materias[clave].get(nrc)

            if materia:
                materia.url = link
                catalogo.actualizar(materia)

            else:
                print(f"Error: El NRC {nrc} no existe en la base de datos.")
                exit(1)
        else:
            print(f"Error: La clave {clave} no existe en la base de datos.")
            exit(1)

    except KeyError:
        import traceback
        print("Error interno: No se encontró un valor necesario para añadir el grupo.")
        print("Detalles:")
        print(traceback.format_exc())
        exit(1)

    return materias


def main():
    clave, nrc, link = verificarArgumentos()
    agregarEnlaceAMaterias(clave, nrc, link)
    generarPagina()


if __name__ == "__main__":
    main()
