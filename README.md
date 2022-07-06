# [Grupos ICOM](https://lordfriky.github.io/grupos_icom)
Página web para facilitar la búsqueda de grupos de WhatsApp de materias

# Cómo usarla
Simplemente entra a la página web, busca la clase en la que estás y entra al grupo de WhatsApp correspondiente. Si aún no ha sido agregado uno y eres el admin de dicho grupo (o tienes el link) puedes agregarlo con el botón ahí mismo, sólo sigue las instrucciones que se muestran en la siguiente página.

# Cómo funciona
La página web está hecha con [*jekyll*](https://jekyllrb.com) (y usa el tema [*Cayman*](https://github.com/pages-themes/cayman)) esto nos permite generar páginas web con Markdown fácilmente. [*GitHub Pages*](https://pages.github.com/) es usado para hostearla gratis (además que también es compatible con *Jekyll*).

En el caso del sistema para agregar los grupos de WhatsApp automáticamente hago uso de [GitHub Actions](https://github.com/features/actions), los cuales se activan por medio de issues abiertos con el prefijo `bot|`, para esto hacemos un workflow que

# To do
Con la funcionalidad actual de la página me basta para lo que quería hacer, sin embargo, si hay mucha demanda en alguno de los siguientes elementos *quizás* trabaje en ellos. De igual manera, los [PR](https://github.com/lordfriky/grupos_icom/compare) son **bienvenidos**.
- [] Agregar un sistema automatizado para generar la página web. (empezado, ver [/tools](https://github.com/lordfriky/grupos_icom/tree/main/tools))
- [] Agregar [octokit](https://github.com/khornberg/octokit.py) para interactuar mejor con los issues.
- [] Agregar los demás semestres.