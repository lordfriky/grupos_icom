# pip3 install validators
from validators import url
from sys import argv
from os.path import exists, join, dirname

if(len(argv) != 4):
    print('Uso: python3 add_link.py *clave_de_materia* *nrc* *link_al_grupo*')
    exit(1)

clave = argv[1]
nrc = argv[2]
link = argv[3]

if len(clave) != 5:
    print('Error: La clave {} es inválida'.format(clave))
    exit(1)

if len(nrc) != 6:
    print('Error: El NRC {} es inválido'.format(nrc))
    exit(1)

# Al parecer las instrucciones no fueron muy claras...
if url.startswith('<'):
    url = url[1:-1]

if not url(link): # To do: Quizás podamos validar que sea un link de WhatsApp, pero igual con esto basta mientras, supongo
    print('Error: El link {} es inválido'.format(link))
    exit(1)

stringAReemplazar = '<a onclick="agregarGrupo(\'{}\', \'{}\')" style="cursor: pointer;"><img src="./res/whatsapp_unavailable.png" width="12"> Agregar</a>'.format(clave, nrc)
stringReemplazada = '<a href="{}" target="_blank"><img src="./res/whatsapp_available.png" width="12"> Link</a>'.format(link)

ruta = dirname(__file__)
ruta = join(ruta, '../index.md')

if not exists(ruta):
    print('Error: No se encontró el archivo index.md')
    exit(1)

with open(ruta, 'r') as file:
    datos = file.readlines()

for i in range(len(datos)):
    if stringAReemplazar in datos[i]:
        datos[i] = datos[i].replace(stringAReemplazar, stringReemplazada)
        encontrado = True
        break

if not encontrado:
    print('Error: No se pudo encontrar la string en el archivo (Quizás el grupo ya fue añadido?)')
    exit(1)

with open(ruta, 'w') as file:
    file.writelines(datos)
    
