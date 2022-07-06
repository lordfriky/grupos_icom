# Uso: python3 get_offer.py *clave_de_materia1_* *clave_de_materia_2* ...
# Todos los demás datos vienen hardcodeados

print("WIP: No funciona")

# pip3 install requests beautifulsoup4
from copyreg import constructor
from sys import argv
from requests import post
from bs4 import BeautifulSoup

if len(argv) < 2:
    print('Uso: python3 get_offer.py *clave_de_materia1_* *clave_de_materia_2* ...')
    exit()

claves = []
for i in argv[1:]:
    if len(i) == 5:
        claves.append(i)
    else:
        print('Error: La clave {} es inválida'.format(i))
        exit(1)

# Datos necesarios para sacar la oferta
url = 'http://consulta.siiau.udg.mx/wco/sspseca.consulta_oferta'
ciclop = '202220' # Calendario 22B
cup = 'D' # CUCEI
majrp = 'ICOM' # Computación, técnicamente no es necesario pero de todos modos lo agrego
mostrarp = '10000' # Número de clases a mostrar, ponemos un valor exagerado para asegurarnos que nos muestre todos
p_start = '0' # Index clases

for clave in claves:
    datos = post(url, data={'ciclop': ciclop, 'cup': cup, 'majrp': majrp, 'crsep': clave, 'mostrarp': mostrarp, 'p_start': p_start})
    
    if datos.status_code != 200:
        print('Error al obtener las clases de {}'.format(clave))
        continue

    # Gracias Diego! (diezep)
    soup = BeautifulSoup(datos.text, 'html.parser')
    tabla = soup.select('tr[bgcolor="A9C0DB"] ~ tr')

    if not tabla:
        print('\nNo hay clases de {}'.format(clave))
        continue
    else:
        print('\nClases de {}'.format(clave))

    nombreMateria = tabla[0].select_one('td:nth-child(3) > a').text
    clases = []

    # Formato: [NRC, Sección, Maestrx, [Horarios], [Días], [Edificios], [Salones]]
    for elemento in tabla:
        constructor = []
        constructor.append(elemento.select_one('td:nth-child(1)').text) # NRC
        print('NRC: {}'.format(constructor[0]))
        constructor.append(elemento.select_one('td:nth-child(4)').text) # Sección
        print('Sección: {}'.format(constructor[1]))
        constructor.append(elemento.select_one('td.tdprofesor:nth-child(2)').text) # Maestrx
        print('Maestrx: {}'.format(constructor[2]))
        Horarios = elemento.select('td:nth-child(8) > table > tr') # Tabla de horarios
        # Hmmm, voy a tener que implementar un sistema para aquellas clases que tienen 2 o más instancias de clases, y 2 o más profesores
        # Meh, luego termino esto, primero voy a dejar la web jalando
