# [Grupos ICOM](https://lordfriky.github.io/grupos_icom)
Página web para facilitar la búsqueda de grupos de WhatsApp de materias.

## Cómo usarla
Simplemente entra a la página web, busca la clase en la que estás y entra al grupo de WhatsApp correspondiente. Si un grupo de WhatsApp aún no ha sido añadido y eres el administrador de dicho grupo (o tienes el enlace), puedes agregarlo con el botón de la misma web, sólo sigue las instrucciones que se muestran en la página. No es necesario que cambies el título ni ningún otro dato, solo coloca el link en donde dice _Enlace de invitación_ y da en submit issue. _**Se requiere una cuenta de GitHub para añadir grupos.**_

## Cómo funciona
La página web está hecha con [*jekyll*](https://jekyllrb.com) (y usa el tema [*Cayman*](https://github.com/pages-themes/cayman)). Esto permite generar páginas web con Markdown fácilmente. Se utiliza [*GitHub Pages*](https://pages.github.com/) para servir la página de manera gratuita (además de que también es compatible con *Jekyll*).

En el caso del sistema para agregar los grupos de WhatsApp, se utiliza [GitHub Actions](https://github.com/features/actions), tareas programadas que se activan al abrir issues con el título ` [BOT] Añadir enlace de invitación`. Si el issue está en el formato correcto, se cerrará atuomáticamente y el grupo aparecerá en la página en cuestión de minutos. Si el issue no está en el formato solicitado, se mantendrá abierto hasta que sea revisado manualmente.

## Por hacer
Con la funcionalidad actual de la página me basta para lo que quería hacer, sin embargo, si hay mucha demanda en alguno de los siguientes elementos *quizás* trabaje en ellos. De igual manera, los [PR](https://github.com/lordfriky/grupos_icom/compare) son **bienvenidos**.
- [x] Agregar un sistema automatizado para generar la página web.
  - Completado
- [ ] Agregar [octokit](https://github.com/khornberg/octokit.py) para interactuar mejor con los issues.
- [x] Agregar los demás semestres.
  - Completado. Queda pendiente subdividirlos


Créditos a SistemaRayoXP por sus aportaciones al repositorio 🤝.
