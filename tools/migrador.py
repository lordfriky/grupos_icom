#!/bin/python3
# coding: utf-8

import os
import json
import xmltodict


def jsonAXml(ruta: str):
    with open(ruta) as f:
        entrada = json.loads(f.read())
    return xmltodict.unparse(entrada, pretty=True)


def cargarJsonMateriasADict(ruta: str):
    dictMaterias = {}

    if os.path.exists(ruta):
        with open(ruta, "r") as f:
            dictMaterias = json.loads(f.read())

    return dictMaterias


def exportarDictAJson(materias: dict, ruta: str):
    with open(ruta, "w") as f:
        f.write(json.dumps(materias, indent=4))


def migrarDictMateriasAVersion2(materias: dict):
    materiasNuevoFormato = {}

    for clave, datos in materias.items():
        materiasNuevoFormato[clave] = {}
        for clase in datos["grupos"].values():
            materiasNuevoFormato[clave][clase["nrc"]] = clase

    return materiasNuevoFormato


if __name__ == "__main__":
    print("Este módulo debe importarse desde la consola interactiva de Python")
