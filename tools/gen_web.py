# To do
import os
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from datetime import datetime
from get_offer import cargarMaterias

RAIZ_WEB = os.path.dirname(os.path.dirname(__file__))


def obtenerMes(mes: int):
    meses = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
        "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ]
    return meses[mes-1]


def procesarMateriasAMarkup(materias: dict):
    document = BeautifulSoup("", "html5lib")
    document.body.append("---\nlayout: default\n---\n")

    for clave, materia in materias.items():
        h2 = document.new_tag("h2", style="text-align: center;")
        h2.string = "{} - {}".format(clave, materia["nombre"])

        document.body.append("\n")
        document.body.append(h2)
        document.body.append("\n\n")
        document.body.append(
            "| NRC | Sección | Maestr@ | Horario | Dias | Edificio | Salón | Grupo de WhatsApp | Eliminada de SIIAU |\n"
            "| --- | ------- | ------- | ------- | ---- | -------- | ----- | ----------------- | ------------------ |\n")

        for grupo in materia["grupos"].values():
            if grupo.get("url"):
                url = grupo.pop("url")
                link = document.new_tag("a", href=url, target="_blank")
                icono = document.new_tag(
                    "img", src="./res/whatsapp_available.png", width="18px")
                link.append(icono)
                link.append(" Enlace de invitación")
            else:
                formatoUrl1 = f"https://github.com/{os.environ.get('GIT_USER', 'lordfriky')}/grupos_icom/issues/new"
                formatoUrl2 = f"?labels=grupo&template=add_group.yml&title={quote_plus('[BOT] Añadir enlace de invitación')}"
                formatoUrl3 = f'&clave={grupo["clave"]}&nrc={grupo["nrc"]}'
                urlIssue = f"{formatoUrl1}{formatoUrl2}{formatoUrl3}"
                link = document.new_tag("a", href=urlIssue, target="_blank")
                icono = document.new_tag(
                    "img", src="./res/whatsapp_unavailable.png", width="18px")
                link.append(icono)
                link.append(" Agregar")

            texto = ""
            carSaltoLinea = "  "
            texto_eliminada = "Eliminada de SIIAU"
            texto_eliminada = texto_eliminada if grupo.get("eliminada") else ""
            orden = [
                grupo["nrc"],
                grupo["seccion"],
                grupo["profesor"],
                grupo["horas"],
                grupo["dias"],
                grupo["edificio"],
                grupo["aula"],
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

    piePagina = document.new_tag("p", class_="text-center text-muted")
    piePagina.string = "Datos actualizados al día "

    ahora = datetime.now()

    fecha = document.new_tag("b")
    fecha.string = f"{ahora.day} de {obtenerMes(ahora.month)} de {ahora.year}"
    piePagina.append(fecha)

    piePagina.append(" a las ")

    hora = document.new_tag("b")
    hora.string = datetime.strftime(ahora, "%I:%M %p")
    piePagina.append(hora)

    document.body.append(piePagina)

    page = str(document.body)
    page = page.replace("<body>", "").replace("</body>", "")

    return page


def guardarPagina(pagina: str, archivo: str = 'index.md'):
    ruta = os.path.join(RAIZ_WEB, archivo)

    with open(ruta, 'w') as file:
        file.write(pagina)


def generarPagina(materias: dict):
    paginaMarkup = procesarMateriasAMarkup(materias)
    guardarPagina(paginaMarkup)


def main():
    print("Generando web...")
    materias = cargarMaterias()
    generarPagina(materias)
    print("Web estática generada correctamente")


if __name__ == "__main__":
    main()
