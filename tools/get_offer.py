# Uso: python3 get_offer.py *clave_de_materia1_* *clave_de_materia_2* ...
# Todos los demás datos vienen hardcodeados

# pip3 install requests beautifulsoup4
import argparse
import os
import re
import sys
import requests
import bs4
import json

# Datos necesarios para obtener la oferta
SERVIDOR_SIIAU = 'http://consulta.siiau.udg.mx'
APP_SIIAU = f'{SERVIDOR_SIIAU}/wco/sspseca.consulta_oferta'
CICLO_ACTUAL = "202220"  # Calendario 22B
CENTRO_DEF = "D"  # CUCEI
CARR_DEF = "ICOM"  # Computación, técnicamente no es necesario pero de todos modos lo agrego
# Número de clases a mostrar, ponemos un valor exagerado para asegurarnos que nos muestre todos
CANT_RESULT_DEF = 10000  # Índice clases
# Ruta al catálogo de materias que contiene los links
RUTA_CATALOGO_MATERIAS = os.path.join(
    os.path.dirname(__file__), "materias.json")

# parser = argparse.ArgumentParser(os.path.basename(__file__))
# parser.add_argument("claves", action=)


if len(sys.argv) < 2:
    print('Uso: python3 get_offer.py *clave_de_materia1_* *clave_de_materia_2* ...')
    exit()


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
        return int(sesion[1:])

    def obtenerHoras(self):
        horas = self.horas
        textoHoras = horas
        if textoHoras.find("-") != -1:
            horasIni = f"{int(horas[0:2]):02d}:{int(horas[2:4]):02d}"
            horasFin = f"{int(horas[5:7]):02d}:{int(horas[7:9]):02d}"
            textoHoras = f"{horasIni} - {horasFin}"

        return textoHoras

    def obtenerDias(self):
        diasSIIAU = self.dias
        dias = []
        diasTexto = {
            "L": "Lunes",
            "M": "Martes",
            "I": "Miércoles",
            "J": "Jueves",
            "V": "Viernes",
            "S": "Sábado",
        }
        diasSIIAU = re.sub(r"[\.\s]+", "", diasSIIAU)
        for letra in diasSIIAU:
            if letra in diasTexto.keys():
                dias.append(diasTexto[letra])

        return ", ".join(dias)

    def obtenerEdificio(self):
        edificio = self.edificio
        centro = self.centro
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
        periodo = self.periodo
        return periodo


class Materia:
    nrc = str()
    clave = str()
    nombre = str()
    seccion = str()
    creditos = int()
    cupo = int()
    disponible = int()
    horarios = []
    profesor = str()

    def __init__(self, nrc: int, clave: str, nombre: str, seccion: str,
                 creditos: int, cupo: int, disponible: int, horarios: list,
                 profesor: str = ""):
        self.nrc = nrc
        self.clave = clave
        self.nombre = nombre
        self.seccion = seccion
        self.creditos = creditos
        self.cupo = cupo
        self.disponible = disponible
        self.horarios = horarios
        self.profesor = profesor

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

    def obtenerProfesor(self):
        return self.profesor.title()

    def obtenerNombre(self):
        return self.nombre.title()


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


def consultaSiiau(ciclo: str = CICLO_ACTUAL,
                  centro: str = CENTRO_DEF,
                  carrera: str = CARR_DEF,
                  materia: str = "",
                  cantResultados: int = CANT_RESULT_DEF,
                  indiceInicio: int = 0):
    materias = []
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
        materias_obj = []

        for entrada in datos:
            horarios = []

            for fila in entrada[8]:
                horario = Horario(centro, fila[0], fila[1], fila[2],
                                  fila[3], fila[4], fila[5])
                horarios.append(horario)

            profesor = entrada[10][0][1] if entrada[10] else ""

            materia_obj = Materia(int(entrada[0]), entrada[1], entrada[2],
                                  entrada[3], int(entrada[4]), int(entrada[5]),
                                  int(entrada[6]), horarios, profesor)
            materias_obj.append(materia_obj)

        for mat in materias_obj:
            mat_legible_por_humanos = {
                "seccion": mat.seccion,
                "materia": mat.obtenerNombre(),
                "cupo": mat.cupo,
                "disponible": mat.disponible,
                "creditos": mat.creditos,
                "nrc": mat.nrc,
                "clave": mat.clave,
                "sesion": mat.obtenerSesion(),
                "horas": mat.obtenerHoras(),
                "dias": mat.obtenerDias(),
                "edificio": mat.obtenerEdificio(),
                "aula": mat.obtenerAula(),
                "periodo": mat.obtenerPeriodo(),
                "profesor": mat.obtenerProfesor(),
                "url": "",
            }
            materias.append(mat_legible_por_humanos)

    return materias


claves = []
for i in sys.argv[1:]:
    if len(i) == 5:
        claves.append(i)
    else:
        print('Error: La clave {} es inválida'.format(i))
        exit(1)

for clave in claves:
    materias = []
    materias.extend(consultaSiiau(materia=clave))
    materias_dict = {}
    for mat in materias:
        if not materias_dict.get(mat["clave"]):
            materias_dict[mat["clave"]] = {
                "nombre": mat["materia"], "grupos": {}}

        materias_dict[mat["clave"]]["grupos"][mat["nrc"]] = mat

    with open(RUTA_CATALOGO_MATERIAS, "rw") as f:
        datos = f.read()
        datos = json.loads(datos)
        datos.update(materias_dict)
        f.write(json.dumps(datos))
