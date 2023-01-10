#!/bin/python3
# coding: utf-8
import os
import datetime as dt

import xml.etree.ElementTree as ET

from urllib.parse import quote_plus
from bs4 import BeautifulSoup

from constantes import *
from CatalogoMaterias import CatalogoMaterias

from get_offer import obtenerPlanes


def obtenerNombreMes(mes: int):
    meses = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
        "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ]
    return meses[mes-1]


def nuevoDocumentoBs():
    document = BeautifulSoup("", "html5lib")
    document.body.append("---\nlayout: default\n---\n")
    
    return document


def obtenerPiePagina(documentoBs: BeautifulSoup):
    piePagina = documentoBs.new_tag("p", class_="text-center text-muted")
    piePagina.string = "Datos actualizados al día "

    zonaHoraria = dt.timezone(dt.timedelta(hours=-5))
    ahora = dt.datetime.now(zonaHoraria)

    fecha = documentoBs.new_tag("b")
    fecha.string = f"{ahora.day} de {obtenerNombreMes(ahora.month)} de {ahora.year}"
    piePagina.append(fecha)

    piePagina.append(" a las ")

    hora = documentoBs.new_tag("b")
    hora.string = dt.datetime.strftime(ahora, "%I:%M %p")
    piePagina.append(hora)
    
    return piePagina


def materiasAMarkup(materias: dict):
    document = nuevoDocumentoBs()

    for clave, materia in materias.items():
        h2 = document.new_tag("h2", style="text-align: center;")
        h2.string = "{} - {}".format(clave, "materia.nombre".title())

        document.body.append("\n")
        document.body.append(h2)
        document.body.append("\n\n")
        document.body.append(
            "| Maestr@ | Dias | Horario | Edificio | Salón | NRC | Sección | Grupo de WhatsApp | Eliminada de SIIAU |\n"
            "| ------- | ---- | ------- | -------- | ----- | --- | ------- | ----------------- | ------------------ |\n")

        for grupo in materia.values():
            if grupo.url:
                link = document.new_tag("a", href=grupo.url, target="_blank")
                icono = document.new_tag(
                    "img", src="./res/whatsapp_available.png", width="18px")
                link.append(icono)
                link.append(" Enlace de invitación")
            else:
                formatoUrl1 = f"https://github.com/{os.environ.get('GIT_USER', 'lordfriky')}/grupos_icom/issues/new"
                formatoUrl2 = f"?labels=grupo&template=add_group.yml&title={quote_plus('[BOT] Añadir enlace de invitación')}"
                formatoUrl3 = f'&clave={grupo.clave}&nrc={grupo.nrc}'
                urlIssue = f"{formatoUrl1}{formatoUrl2}{formatoUrl3}"
                link = document.new_tag("a", href=urlIssue, target="_blank")
                icono = document.new_tag(
                    "img", src="./res/whatsapp_unavailable.png", width="18px")
                link.append(icono)
                link.append(" Agregar")

            texto = ""
            carSaltoLinea = "  "
            texto_eliminada = "Eliminada de SIIAU"
            texto_eliminada = texto_eliminada if grupo.eliminada else ""
            orden = [
                grupo.obtenerProfesor(),
                grupo.obtenerDias,
                grupo.obtenerHoras(),
                grupo.obtenerEdificio(),
                grupo.obtenerAula(),
                grupo.seccion,
                grupo.nrc,
            ]

            for val in orden:
                if val:
                    if isinstance(val, list):
                        # Por si se cuela algún número
                        val = [str(x) for x in val]
                        valor = carSaltoLinea.join(val)
                    else:
                        valor = val
                else:
                    valor = "N/D"
                texto += f"| {valor} "

            texto += "| "

            document.body.append(texto)
            document.body.append(link)
            document.body.append(" | ")
            document.body.append(texto_eliminada)
            document.body.append(" |\n")

    document.body.append("\n")

    document.body.append(obtenerPiePagina(document))

    return document


def generarPaginasSemestres(mallas: list[ET.Element], plan: str, rutaPlan: str):
    document = nuevoDocumentoBs()
    catalogo = CatalogoMaterias(plan)
    haySemestresAgregados = False

    for mallaTag in mallas:
        nombreMalla = mallaTag.attrib['nombre']
        idMalla = mallaTag.attrib['id']

        h2 = document.new_tag("h2", style="text-align: center;")
        h2.string = f"Malla {nombreMalla}"

        document.body.append("\n")
        document.body.append(h2)
        document.body.append("\n\n")
        document.body.append("| Semestre |\n"
                             "| -------- |\n")
        semestresMalla = mallaTag.findall("semestre")
        semestresMalla = sorted(semestresMalla,
                                key=lambda m: m.attrib["numero"])

        for semestre in semestresMalla:
            numSemestre = semestre.attrib['numero']
            rutaSemestre = f"{rutaPlan}/{idMalla}/{numSemestre}"
            claves = semestre.findall("materia")
            claves = [c.text for c in claves]

            materias = {
                clave: catalogo.obtenerPorClave(clave) for clave in claves
            }

            # Si al menos una materia tiene secciones, hacemos el semestre
            if any(list(materias.values())):
                haySemestresAgregados = True
                hrefSemestre = f"{idMalla}/{numSemestre}"
                enlaceSemestre = document.new_tag("a", href=hrefSemestre)
                enlaceSemestre.string = f"{numSemestre}º"
                document.body.append("| ")
                document.body.append(enlaceSemestre)
                document.body.append(" |\n")
                documentoSemestre = materiasAMarkup(materias)
                guardarPagina(documentoSemestre, f"{rutaSemestre}/index.md")

            # Si ningún elemento tiene secciones,
            # borramos la carpeta (si existe) y saltamos
            else:
                if os.path.exists(rutaSemestre):
                    os.rmdir(rutaSemestre)
                continue

    document.body.append("\n")
    document.body.append(obtenerPiePagina(document))
    
    return document if haySemestresAgregados else None


def generarPlanes():
    document = nuevoDocumentoBs()
    planes = obtenerPlanes()

    for planTag in planes:
        idPlan = planTag.attrib["id"]
        mallas = planTag.findall("malla")
        rutaPlan = f"planes/{idPlan}"
        enlacePlan = document.new_tag("a")
        enlacePlan["style"] = "padding: 1rem;"
        enlacePlan["href"] = f"{rutaPlan}/"
        enlacePlan.string = idPlan
        document.body.append(enlacePlan)

        documentoSemestres = generarPaginasSemestres(mallas, idPlan, rutaPlan)
        if documentoSemestres is not None:
            guardarPagina(documentoSemestres, f"{rutaPlan}/index.md")

    document.body.append("\n")
    document.body.append(obtenerPiePagina(document))
    
    return document


def generarPagina():
    generacionCorrecta = True
    try:
        paginaPlanes = generarPlanes()
        guardarPagina(paginaPlanes, "index.md")

    except:
        import traceback
        print(traceback.format_exc())
        generacionCorrecta = False

    return generacionCorrecta


def guardarPagina(documento: BeautifulSoup, archivo: str):
    ruta = os.path.join(RAIZ_WEB, archivo)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)

    paginaMd = str(documento.body)
    paginaMd = paginaMd.replace("<body>", "").replace("</body>", "")

    with open(ruta, 'w') as file:
        file.write(paginaMd)


def main():
    print("Generando web...")
    if generarPagina():
        print("Archivos estáticos generados correctamente")
    else:
        print("Error al generar los archivos estáticos")


if __name__ == "__main__":
    main()
