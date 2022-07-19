# Uso: python3 get_offer.py *clave_de_materia1_* *clave_de_materia_2* ...
# Todos los demás datos vienen hardcodeados

# pip3 install requests beautifulsoup4
import argparse
import os
import re
import requests
import bs4
import json

# Datos necesarios para obtener la oferta
SERVIDOR_SIIAU = 'http://consulta.siiau.udg.mx'
APP_SIIAU = f'{SERVIDOR_SIIAU}/wco/sspseca.consulta_oferta'
CICLO_ACTUAL = "202220"  # Calendario 22B
CENTRO_DEF = "D"  # CUCEI
PLAN_DEF = "ICOM"  # Computación, técnicamente no es necesario pero de todos modos lo agrego
# Número de clases a mostrar, ponemos un valor exagerado para asegurarnos que nos muestre todos
CANT_RESULT_DEF = 10000  # Índice clases
# Ruta al catálogo de materias que contiene los links
RUTA_CATALOGO_MATERIAS = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "materias.json")


class Horario:
    horarios = list()
    centro = str()
    sesion = str()
    horas = str()
    dias = str()
    edificio = str()
    aula = str()
    periodo = str()

    def __init__(self, centro: str, sesion: str, horas: str, dias: str, edificio: str, aula: str, periodo: str):
        self.centro = centro
        self.sesion = sesion
        self.horas = horas
        self.dias = dias
        self.edificio = edificio
        self.aula = aula
        self.periodo = periodo

    def obtenerSesion(self):
        sesion = self.sesion
        sesion = sesion if isinstance(sesion, int) else int(sesion[1:])
        return sesion

    def obtenerHoras(self):
        horas = self.horas
        textoHoras = horas
        if textoHoras.find("-") != -1 and textoHoras.find(":") == -1:
            horasIni = f"{int(horas[0:2]):02d}:{int(horas[2:4]):02d}"
            horasFin = f"{int(horas[5:7]):02d}:{int(horas[7:9]):02d}"
            textoHoras = f"{horasIni} - {horasFin}"

        return textoHoras

    def obtenerDias(self):
        dias = []
        diasTexto = self.dias
        if "." in diasTexto:
            diasClave = {
                "L": "Lunes",
                "M": "Martes",
                "I": "Miércoles",
                "J": "Jueves",
                "V": "Viernes",
                "S": "Sábado",
            }
            diasSIIAU = re.sub(r"[\.\s]+", "", diasTexto)
            for letra in diasSIIAU:
                if letra in diasClave:
                    dias.append(diasClave[letra])
            diasTexto = ", ".join(dias)

        return diasTexto

    def obtenerEdificio(self):
        edificio = self.edificio
        centro = self.centro
        if not ("Edificio" in edificio and "Virtual" in edificio):
            coincVirt = re.match(fr"^{centro}ESV|^VIRTU\w*", edificio)
            if coincVirt is not None:
                edificio = re.sub(fr"^{centro}ESV|^VIRTU\w*", "", edificio)
                edificio = f"Virtual {edificio}"
            else:
                edificio = re.sub(fr"^{centro}(ED)?", "", edificio)
                edificio = f"Edificio {edificio}"
        return edificio

    def obtenerAula(self):
        aula = self.aula
        textoAula = aula
        partes_aula = re.match("([A-Za-z]+)(\d+)", aula)
        if partes_aula is not None:
            alfa = partes_aula[1]
            num = int(partes_aula[2])
            textoAula = f"{alfa}{num:02d}"

        return textoAula

    def obtenerPeriodo(self):
        return self.periodo


class Materia:
    centro = str()
    nrc = str()
    clave = str()
    nombre = str()
    seccion = str()
    creditos = int()
    cupo = int()
    disponible = int()
    horarios = []
    profesor = str()
    url = str()
    eliminada = False

    def __init__(self, centro: str, nrc: int, clave: str, nombre: str,
                 seccion: str, creditos: int, cupo: int, disponible: int,
                 horarios: list, profesor: str = "", eliminada: bool = False,
                 url: str = ""):
        self.centro = centro
        self.nrc = nrc
        self.clave = clave
        self.nombre = nombre.upper()
        self.seccion = seccion
        self.creditos = creditos
        self.cupo = cupo
        self.disponible = disponible
        self.horarios = horarios
        self.profesor = profesor.upper()
        self.url = url
        self.eliminada = eliminada

    def indiceValido(self, i, lista):
        return (i is not None and 0 <= i < len(lista))

    def obtenerSesion(self, indiceHorario=None, legible_por_humanos=True):
        sesion = []
        if (self.indiceValido(indiceHorario, self.horarios)):
            horario = self.horarios[indiceHorario]
            sesion = horario.obtenerSesion()
        else:
            for horario in self.horarios:
                if (legible_por_humanos):
                    sesion.append(horario.obtenerSesion())
                else:
                    sesion.append(horario.sesion)

        return sesion

    def obtenerHoras(self, indiceHorario=None, legible_por_humanos=True):
        horas = []
        if (self.indiceValido(indiceHorario, self.horarios)):
            horario = self.horarios[indiceHorario]
            horas = horario.obtenerHoras()
        else:
            for horario in self.horarios:
                if (legible_por_humanos):
                    horas.append(horario.obtenerHoras())
                else:
                    horas.append(horario.horas)

        return horas

    def obtenerDias(self, indiceHorario=None, legible_por_humanos=True):
        dias = []
        if self.indiceValido(indiceHorario, self.horarios):
            horario = self.horarios[indiceHorario]
            dias = horario.obtenerDias()
        else:
            for horario in self.horarios:
                if legible_por_humanos:
                    dias.append(horario.obtenerDias())
                else:
                    dias.append(horario.dias)
        return dias

    def obtenerEdificio(self, indiceHorario=None, legible_por_humanos=True):
        edificios = []
        if (self.indiceValido(indiceHorario, self.horarios)):
            horario = self.horarios[indiceHorario]
            edificios = horario.obtenerEdificio()
        else:
            for horario in self.horarios:
                if legible_por_humanos:
                    edificios.append(horario.obtenerEdificio())

                else:
                    edificios.append(horario.edificio)

        return edificios

    def obtenerAula(self, indiceHorario=None, legible_por_humanos=True):
        aulas = []
        if self.indiceValido(indiceHorario, self.horarios):
            horario = self.horarios[indiceHorario]
            aulas = horario.obtenerAula()
        else:
            for horario in self.horarios:
                if legible_por_humanos:
                    aulas.append(horario.obtenerAula())
                else:
                    aulas.append(horario.aula)
        return aulas

    def obtenerPeriodo(self, indiceHorario=None, legible_por_humanos=True):
        periodos = []
        if self.indiceValido(indiceHorario, self.horarios):
            horario = self.horarios[indiceHorario]
            periodos = horario.obtenerPeriodo()
        else:
            for horario in self.horarios:
                if legible_por_humanos:
                    periodos.append(horario.obtenerPeriodo())
                else:
                    periodos.append(horario.periodo)
        return periodos

    def obtenerNombre(self):
        return self.nombre.title()

    def obtenerProfesor(self):
        return self.profesor.title()

    def obtenerVersionHumana(self):
        """Devuelve un diccionario con los detalles de la materia en formato legible por humanos"""
        mat_legible_por_humanos = {
            "centro": self.centro,
            "seccion": self.seccion,
            "materia": self.obtenerNombre(),
            "cupo": self.cupo,
            "disponible": self.disponible,
            "creditos": self.creditos,
            "nrc": self.nrc,
            "clave": self.clave,
            "sesion": self.obtenerSesion(),
            "horas": self.obtenerHoras(),
            "dias": self.obtenerDias(),
            "edificio": self.obtenerEdificio(),
            "aula": self.obtenerAula(),
            "periodo": self.obtenerPeriodo(),
            "profesor": self.obtenerProfesor(),
            "url": self.url,
            "eliminada": self.eliminada,
        }
        return mat_legible_por_humanos


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


def guardarMaterias(materiasAGuardar: dict | list):
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


def extraerDatosTabla(tabla: bs4.Tag | bs4.NavigableString, saltarFilasInvalidas: bool = False, cantCeldasEsperadas: int = 0):
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
