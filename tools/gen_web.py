# To do
import os
from bs4 import BeautifulSoup
from datetime import datetime

RAIZ_WEB = os.path.dirname(os.path.dirname(__file__))

def obtenerMes(mes: int):
    meses = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
        "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ]
    return meses[mes]


def procesarMateriasAMarkup(materias: dict):
    document = BeautifulSoup("", "html5lib")
    document.body.append("---\nlayout: default\n---\n")

    for clave, materia in materias.items():
        h2 = document.new_tag("h2", style="text-align: center;")
        h2.string = "{} - {}".format(clave, materia["nombre"])

        document.body.append("\n")
        document.body.append(h2)
        document.body.append("\n\n")
        document.body.append("| NRC | Sección | Maestr@ | Horario | Dias | Edificio | Salón | Grupo de WhatsApp |\n")
        document.body.append("| --- | ------- | ------- | ------- | ---- | -------- | ----- | ----------------- |\n")

        for grupo in materia["grupos"].values():
            url = grupo.pop("url")
            if url:
                link = document.new_tag("a", href=url, target="_blank")
                icono = document.new_tag("img", src="./res/whatsapp_available.png", width="18px")
                link.append(icono)
                link.append(" Enlace de invitación")
            else:
                formatoUrl = "https://github.com/{}/grupos_icom/issues/new?labels=grupo&template=add_group.yml&title=%5BBOT%5D+A%C3%B1adir+enlace+de+invitaci%C3%B3n&clave={}&nrc={}"
                urlIssue = formatoUrl.format(os.environ.get("GIT_USER"), grupo["clave"], grupo["nrc"])
                link = document.new_tag("a", href=urlIssue, target="_blank")
                icono = document.new_tag("img", src="./res/whatsapp_unavailable.png", width="18px")
                link.append(icono)
                link.append(" Agregar")

            formato = "| {} | {} | {} | {} | {} | {} | {} | "
            carSaltoLinea = "  "

            texto = formato.format(grupo["nrc"], grupo["seccion"], grupo["profesor"], carSaltoLinea.join(grupo["horas"]),
                                   carSaltoLinea.join(grupo["dias"]), carSaltoLinea.join(grupo["edificio"]), carSaltoLinea.join(grupo["aula"]))

            document.body.append(texto)
            document.body.append(link)
            document.body.append(" |\n")

    document.body.append("\n")

    piePagina = document.new_tag("p", class_="text-center text-muted")
    piePagina.string = "Datos actualizados al día "

    ahora = datetime.now()
    mes = obtenerMes(ahora.month)

    fecha = document.new_tag("b")
    fecha.string = datetime.strftime(ahora, f"{ahora.day} de {mes} de %Y")
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
