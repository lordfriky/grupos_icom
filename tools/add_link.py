# pip3 install bs4 html5lib
import json
import os
import re
from sys import argv
from .gen_web import generarPagina


RAIZ_WEB = os.path.dirname(os.path.dirname(__file__))
RUTA_MATERIAS = os.path.join(RAIZ_WEB, "materias.json")

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


def main(args):
    clave, nrc, link = verificarArgumentos(args)
    materias = agregarEnlaceAMaterias(clave, nrc, link)
    generarPagina(materias)


if __name__ == "__main__":
    main(argv)
    
