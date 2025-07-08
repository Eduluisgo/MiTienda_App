# MiTienda_App

Mi Tienda
¡Tu app móvil para gestionar tiendas, hecha con Kivy y KivyMD!

Lo que puedes hacer
Gestionar productos (añadir, editar, borrar).

Organizar productos por categorías.

Administrar información de clientes.

Interfaz moderna y fácil de usar.


¿Cómo la instalo y la uso?
Para desarrolladores (en Windows con WSL):
Prepárate: Necesitas WSL2 (Ubuntu 22.04 LTS), VS Code (con extensión WSL), Python 3, pip, Git.

Clona el proyecto:

Abre tu terminal de Ubuntu en WSL.

Ve a tu carpeta personal (cd ~).

Entra a la carpeta: cd MiTienda

Abre en VS Code:

Desde la terminal WSL, escribe code . (esto la abrirá correctamente).

Instala dependencias:

En la terminal de VS Code (dentro de WSL): pip install kivy kivymd buildozer cython==0.29.36

Y también: sudo apt update && sudo apt install -y git build-essential zlib1g-dev libncurses5-dev libffi-dev libssl-dev pkg-config libsdl2-dev libtool autoconf automake libpng-dev libjpeg-dev unzip

Configura Buildozer:

buildozer init

Edita el archivo buildozer.spec para poner el nombre de tu app, la versión, los permisos, etc. (revisa package.name, title, requirements, android.permissions).

Para generar la APK (el instalador para Android):
Limpia lo anterior: En la terminal de VS Code (dentro de WSL, en la carpeta del proyecto): buildozer android clean

Crea la APK: buildozer -v android debug (esto tardará un poco la primera vez).
