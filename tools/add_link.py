# pip3 install bs4
from datetime import datetime
import json
import os
import re
from sys import argv
from bs4 import BeautifulSoup


RAIZ_WEB = os.path.dirname(os.path.dirname(__file__))
RUTA_MATERIAS = os.path.join(RAIZ_WEB, "materias.json")

def obtenerMes(mes: int):
    meses = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
        "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ]
    return meses[mes]


def verificarArgumentos(argumentos: list):
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

    elif len(argumentos) == 4:
        clave, nrc, link = argv[1:4]

    else:
        print('Uso: python3 add_link.py *clave_de_materia* *nrc* *link_al_grupo*')
        exit(1)

    if not os.environ.get("GIT_USER"):
        print("La variable de entorno 'GIT_USER' no está establecida. Imposible continuar")
        exit(1)

    if len(clave) != 5:
        print('Error: La clave {} es inválida.'.format(clave))
        exit(1)

    if len(nrc) != 6:
        print('Error: El NRC {} es inválido.'.format(nrc))
        exit(1)

    # Limpiamos por si las instrucciones no fueron claras
    link = link.strip("<>")

    # Validamos que sea un link de WhatsApp
    if re.match(r"https://(?:www\.)?chat\.whatsapp\.com/[\w]+", link) is None:
        print('Error: El link {} es inválido. Verifica que el link comience con HTTPS y no HTTP'.format(link))
        exit(1)

    return clave, nrc, link


def agregarEnlaceAMaterias(clave: str, nrc: str, link: str):
    materias = cargarMaterias()
    if not materias:
        exit(1)

    try:
        if materias.get(clave, {}):
            if materias[clave]["grupos"].get(nrc):
                materias[clave]["grupos"][nrc]["url"] = link
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

    if not guardarMaterias(materias):
        exit(1)

    return materias


def cargarMaterias():
    materias = {}
    try:
        with open(RUTA_MATERIAS, "r") as f:
            materias = f.read()

        materias = json.loads(materias)
    except Exception:
        import traceback
        print("Error: No se pudieron cargar las materias del JSON")
        print("Detalles:")
        print(traceback.format_exc())

    return materias


def guardarMaterias(materias: dict):
    correcto = True
    try:
        with open(RUTA_MATERIAS, "w") as f:
            f.write(json.dumps(materias, indent=4))
    except Exception:
        correcto = False
        import traceback
        print("Error: No se pudieron guardar las materias en el JSON")
        print("Detalles:")
        print(traceback.format_exc())

    return correcto


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


def main(args):
    clave, nrc, link = verificarArgumentos(args)
    materias = agregarEnlaceAMaterias(clave, nrc, link)
    paginaMarkup = procesarMateriasAMarkup(materias)
    guardarPagina(paginaMarkup)


if __name__ == "__main__":
    main(argv)
    
