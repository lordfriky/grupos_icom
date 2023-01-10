# Data
Aquí se guardan los datos que se usan para generar la web y otras cosas.

Si se desea añadir otro plan de estudios (como INCO, INNI, etc), sigue estos pasos:
- Añade los datos en el XML planes.xml, tomando de ejemplo lo que ya existe
  - Dentro de la raíz &lt;planes&gt; añadir una etiqueta &lt;plan&gt; con atributo "id" y el id del plan (ej. INCO)
  - Dentro de &lt;plan&gt; añadir una o más etiquetas &lt;malla&gt; con 2 atributos: "nombre" e "id". Primero añadir la malla oficial de coordinación con nombre e id "Oficial" (seguir el ejemplo de ICOM)
- Ejecutar "python3 get_offer.py" seguido de "python3 gen_web.py" para actualizar la oferta de todos los planes y crear las páginas para los grupos respectivos
  - Se crearán páginas solo para semestres que tengan materias con secciones en SIIAU
    - Si en un nuevo plan no hay 6to aún, o en un viejo plan 2do desapareció, no se mostrarán dichos semestres en la página 