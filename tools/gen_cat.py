#!/bin/python3
# coding: utf-8

from get_offer import CENTRO_DEF
import os
import json
import Materia
import Horario

# Ruta al catálogo de materias que contiene los links
RUTA_CATALOGO_MATERIAS = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "materias.json")

def cargarMaterias(clasificarMaterias: bool = True, objetosMateria: bool = False):
    materias_cargadas = {}
    try:
        if os.path.exists(RUTA_CATALOGO_MATERIAS):
            with open(RUTA_CATALOGO_MATERIAS, "r") as f:
                materias_cargadas = json.loads(f.read())
            if objetosMateria or not clasificarMaterias:
                materias_cargadas = aplanarDictMaterias(materias_cargadas)
            if objetosMateria:
                materias_cargadas = dictAMaterias(
                    materias_cargadas, clasificarMaterias)

    except Exception:
        import traceback
        print("Error: No se pudieron cargar las materias del JSON")
        print("Detalles:")
        print(traceback.format_exc())

    return materias_cargadas


def guardarMaterias(materiasAGuardar):
    """
    Guarda una lista de objetos materia, una lista de dicts
    de materias, o un dict con la estructura de catálogo
    en el JSON de materias
    """
    correcto = True
    try:
        if isinstance(materiasAGuardar, list) and materiasAGuardar:
            if materiasAGuardar and isinstance(materiasAGuardar[0], Materia):
                materiasAGuardar = materiasADict(materiasAGuardar)
            # Convertimos la lista de materias a un dict ordenado por clave y NRC
            materiasAGuardar = clasificarMateriasEnDict(materiasAGuardar)
        with open(RUTA_CATALOGO_MATERIAS, "w") as f:
            f.write(json.dumps(materiasAGuardar, indent=4))

    except Exception:
        correcto = False
        import traceback
        print("Error: No se pudieron guardar las materias en el JSON")
        print("Detalles:")
        print(traceback.format_exc())

    return correcto


def actualizarMaterias(materiasNuevas: dict, materiasAnteriores: dict):
    materias_exportar = {}
    # Iteramos sobre las materias nuevas para añadir/actualizar
    for nrc, mat_nva in materiasNuevas.items():
        # Verificamos si la materia nueva ya existía
        # en la oferta para actualizarla

        if nrc in materiasAnteriores.keys():
            # Obtenemos la materia actual
            mat_act = materiasAnteriores[nrc]
            # Establecemos la url (o lo que tenía) la otra materia
            mat_nva.url = mat_act.url
            # Añadimos la materia
            materias_exportar[nrc] = mat_nva

        else:
            # No existía, simplemente añadimos la materia
            materias_exportar[nrc] = mat_nva

    return materias_exportar


def obtenerMatsEliminadas(materiasAnteriores: dict, materiasActuales: dict):
    materias_eliminadas = {}
    # Iteramos sobre las materias actuales para ver cuáles ya no existen
    for nrc, mat_ant in materiasAnteriores.items():
        # Si no existe el NRC en las materias obtenidas de SIIAU, la borraron
        if not nrc in materiasActuales.keys():
            # Avisamos que la borraron
            mat_ant.eliminada = True
            # La añadimos a las que borraron
            materias_eliminadas[nrc] = mat_ant

    return materias_eliminadas


def materiasADict(materias: list, clasificarPorNrc: bool = False):
    materias_dict = {} if clasificarPorNrc else []
    for mat in materias:
        if not isinstance(mat, Materia):
            continue
        mat_humana = mat.obtenerVersionHumana()
        if clasificarPorNrc:
            materias_dict[mat.nrc] = mat_humana
        else:
            materias_dict.append(mat_humana)
    return materias_dict


def dictAMaterias(materias: list, clasificarPorNrc: bool = False):
    materias_obj = {} if clasificarPorNrc else []
    for mat in materias:
        req_keys = ['seccion', 'materia', 'cupo', 'disponible', 'creditos',
                    'nrc', 'clave', 'sesion', 'horas', 'dias', 'edificio',
                    'aula', 'periodo', 'profesor', 'url']
        if not (isinstance(mat, dict) or req_keys in mat.keys()):
            continue
        horarios = []
        # El valor por defecto no debería de obtenerse
        centro = mat.get("centro", CENTRO_DEF)

        for i in range(len(mat["sesion"])):
            sesion = mat["sesion"][i]
            horas = mat["horas"][i]
            dias = mat["dias"][i]
            edif = mat["edificio"][i]
            aula = mat["aula"][i]
            periodo = mat["periodo"][i]
            horario = Horario(centro, sesion, horas, dias, edif, aula, periodo)
            horarios.append(horario)

        materia_obj = Materia(centro, mat["nrc"], mat["clave"],
                              mat["materia"], mat["seccion"], mat["creditos"],
                              mat["cupo"], mat["disponible"], horarios,
                              mat["profesor"], mat.get("eliminada", False), mat["url"])
        if clasificarPorNrc:
            materias_obj[materia_obj.nrc] = materia_obj
        else:
            materias_obj.append(materia_obj)
    return materias_obj


def clasificarMateriasEnDict(listaMaterias: list):
    materias_clasificadas = {}
    for mat in listaMaterias:
        if not materias_clasificadas.get(mat["clave"]):
            materias_clasificadas[mat["clave"]] = {
                "nombre": mat["materia"], "grupos": {}}
        materias_clasificadas[mat["clave"]]["grupos"][mat["nrc"]] = mat
    return materias_clasificadas


def aplanarDictMaterias(dictMaterias: dict, retornarDict: bool = False):
    materias_planas = {}
    for materia in dictMaterias.values():
        for grupo in materia["grupos"].values():
            materias_planas[grupo["nrc"]] = grupo
    return list(materias_planas.values()) if not retornarDict else materias_planas


def generarCatalogoMaterias(materiasNuevas: list, conservar_materias_eliminadas: bool = True):
    # Hay catálogo de materias ya existente
    if os.path.exists(RUTA_CATALOGO_MATERIAS):
        # Indizamos las materias en un dict tipo {"nrc": materia...}
        materias_actuales_obj = cargarMaterias(objetosMateria=True)
        # Diccionario por comprensión
        materias_nuevas_obj = {mat.nrc: mat for mat in materiasNuevas}
        # Aquí se almacenarán las materias que vamos a exportar
        materias_exportar = actualizarMaterias(
            materias_nuevas_obj, materias_actuales_obj)

        # Usualmente no queremos conservar las materias
        # cuando ya empezó el ciclo y no las restablecieron
        # De otro modo, puede que las restablezcan y hay que
        # conservarlas
        if conservar_materias_eliminadas:
            materias_exportar.update(
                obtenerMatsEliminadas(materias_actuales_obj,
                                      materias_exportar))

        # Convertimos el dict en lista para posterior procesamiento
        materias = list(materias_exportar.values())

    # No hay catálogo de materias y es el primero que generamos
    else:
        materias = materiasNuevas

    # Guardamos el catálogo
    guardarMaterias(materias)
