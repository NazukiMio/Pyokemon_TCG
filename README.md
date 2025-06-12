# Pyokemon TCG - Descripción General del Proyecto (Python/PyGame)

(Para la versión en chino, ver [README_CN.md](README_CN.md). Para la versión en español, ver [README_ES.md](README.md).)

## Introducción al Proyecto

**Pyokemon TCG** es un simulador no oficial del juego de cartas coleccionables de Pokémon, desarrollado con Python y PyGame con fines educativos. Es un proyecto sin ánimo de lucro que busca ayudar a los principiantes a aprender desarrollo de videojuegos replicando las mecánicas básicas del TCG de Pokémon. Pyokemon TCG sirve como ejemplo didáctico integral, demostrando cómo construir un juego completo incluyendo inicio de sesión de usuario, interfaz gráfica, lógica por turnos y recuperación de datos mediante API. Adopta una arquitectura modular y prácticas de código limpio, lo que lo hace jugable y fácil de entender — ideal para quienes aprenden desarrollo de juegos con Python.

## Resumen de Funcionalidades

- **Registro e Inicio de Sesión de Usuarios**: El sistema permite registrar nuevos usuarios e iniciar sesión con cuentas existentes. Los perfiles y el progreso del jugador se guardan localmente en una base de datos SQLite. El proceso de autenticación está gestionado por `AuthManager`, que utiliza autenticación basada en tokens para intercambiar datos de forma segura sin pasar credenciales entre escenas.
- ![Página de Bienvenida](assets/images/markdown/welcome.png)
- ![Inicio de Sesión](assets/images/markdown/login.png)
- ![Registro](assets/images/markdown/register.png)

- **Pokédex de Cartas**: Interfaz visual que muestra todas las cartas Pokémon obtenidas. Los jugadores pueden navegar por miniaturas y aplicar filtros por propiedad, rareza, tipo, entre otros. Para optimizar el rendimiento, se implementa caché de imágenes, lo que permite renderizar fluidamente incluso con muchas cartas.

- ![Pokédex de Cartas](assets/images/markdown/pokedex.png)

- **Navegación de Interfaz y Cambio de Escena**: El juego ofrece una barra de navegación unificada que permite transiciones fluidas entre escenas como Inicio, Pokédex, Tienda y Preparación de Batalla. Ubicada generalmente en la parte superior o inferior de la ventana, incluye botones icónicos para cada módulo. Cada escena (inicio de sesión, principal, batalla) es un módulo independiente, garantizando separación de lógica y experiencia fluida.
- ![Interfaz Principal](assets/images/markdown/mainscene.png)

- **Compra y Apertura de Sobres**: Simula la experiencia de comprar y abrir sobres de cartas Pokémon. Los jugadores pueden adquirir sobres en la **Tienda** con moneda virtual y abrirlos con efectos animados. Al hacer clic en un sobre cerrado, se "rasga" la envoltura y se muestran cartas aleatorias obtenidas. Esta mecánica imita la emoción del mundo real.
- ![Abrir Sobre](assets/images/markdown/open_pack.png)

- **Almacenamiento Local de Datos**: El progreso del juego (usuarios, cartas, mazos, estadísticas) se guarda localmente mediante SQLite. Los datos de cartas también se almacenan en archivos JSON, permitiendo jugar sin conexión tras la primera configuración. No se necesita conexión persistente.

- **Herramienta de Descarga de Cartas**: La herramienta independiente `fetch_card_gui` permite importar cartas desde la API oficial del TCG de Pokémon. Con una GUI simple, se pueden establecer parámetros como cantidad de cartas y carpeta de destino. Descarga metadatos e imágenes, generando `cards.json` e imágenes locales para el juego. Ideal para docentes o desarrolladores que deseen actualizar el conjunto de cartas.
- ![Herramienta de Descarga](assets/images/markdown/fetch_card_gui.png)

- **Constructor de Mazos (En Desarrollo)**: Se está desarrollando un editor de mazos que permitirá construir y guardar mazos personalizados con las cartas obtenidas. Incluirá filtros, agregar/quitar cartas y múltiples perfiles guardados.

- **Sistema de Batalla Local (En Desarrollo)**: Se planea un modo de batalla 1v1 local. La lógica por turnos está implementada y se está integrando la GUI. Usa `pygame-cards` para interacciones visuales y `pygame-gui` para acciones como atacar o usar energía. El diseño modular separa lógica y UI, facilitando soporte futuro para juego en línea.

- **Expansiones Futuras**: Gracias a su diseño modular, Pyokemon TCG está preparado para futuras funciones como ampliación de tienda (ítems, misiones), modos en línea (PvP, intercambio) y funciones sociales (amigos, chat). Aunque aún no están implementadas, la arquitectura ya lo permite.

## Instalación y Dependencias

**Entorno Requerido**: Python 3.10 o superior. Se recomienda usar un entorno virtual para evitar conflictos con paquetes globales. Las dependencias externas incluyen:

***Debido a conflictos entre `pygame-gui` y `pygame-cards`, NO instalar usando `pip install -r requirements.txt`. Este archivo es solo de referencia.***

***Si no sabes cómo resolver conflictos, usa la herramienta de inicio para [Windows](install_env_start_windows.bat) o [Linux](install_env_start_linux.sh).***

**Dependencias Principales**:

- **pygame** – Motor 2D para gestión de ventanas, eventos y renderizado.
- **pygame-gui** – Framework de GUI sobre PyGame, usado para botones, entradas y menús.
- **pygame-cards** – Librería para mostrar/interactuar con cartas (arrastrar, voltear); usada en batallas.
- **requests** – Para comunicación HTTP con la API de Pokémon TCG.
- **Pillow (PIL)** – Procesamiento de imágenes para redimensionar y convertir formatos.

**Herramientas de Inicio**:

- [Script para Windows](install_env_start_windows.bat)
- [Script para Linux](install_env_start_linux.sh)

**Librerías de Desarrollo Adicionales**:

- `tkinter` – Para la GUI del descargador (incluido por defecto)
- `opencv-python` – Procesamiento de imagen (herramientas de desarrollo)
- `graphviz` – Generación de árbol de directorios
- `tqdm` – Barras de progreso en consola

**SQLite**: Incluido con Python.

**Uso de Herramientas de Desarrollo**:

Para actualizar las cartas o con fines didácticos, usa la herramienta de descarga en `development/fetch_card/`. Lanza la GUI con:

```bash
python development/fetch_card/fetch_card_gui.py
```

Establece parámetros como número de cartas y carpeta de salida, luego haz clic en iniciar. Los datos se guardan en `card_assets/cards.json` y las imágenes en `card_assets/images/`. Asegúrate de que el juego esté cerrado durante la actualización. Una sola importación suele bastar para jugar offline.

Otros scripts de desarrollo (generador de árbol de carpetas, revisión de fuentes del sistema, herramientas de imagen) pueden ejecutarse manualmente. No son necesarios para jugar.

## Estructura del Proyecto

El proyecto está organizado por funcionalidad, separando lógica, recursos y herramientas. Estructura principal:

- `game/`: Lógica principal: autenticación, base de datos, batallas.

```
game/
├── core/        # Módulos principales (Autenticación, BD, Batalla, etc.)
├── scenes/      # Definiciones de escenas (Inicio de sesión, Inicio, Pokédex, Batalla)
│   ├── login_scene.py
│   ├── dex_page.py
│   └── battle_page.py
├── ui/          # Componentes reutilizables de interfaz gráfica
│   ├── navigation_bar/
│   └── battle_interface/
├── utils/
│   └── video_background.py
```

- `assets/`: Recursos gráficos y de sonido.

```
assets/
├── images/     # Fondos, arte de cartas, etc.
├── icons/      # Iconos de la interfaz
├── fonts/      # Archivos de fuentes
├── sounds/     # Efectos de sonido y música
├── videos/     # Cinemáticas
├── json/       # Datos de imagen
```

- `data/`: Datos locales (progreso, usuarios).

```
data/
├── game_database.db  # Base de datos SQLite
├── cards.json        # Datos de cartas (extraídos)
└── cache/            # Imágenes escaladas en caché
```

- `development/`: Herramientas de desarrollo (opcional).

```
development/
├── fetch_card/             # Herramienta de descarga de cartas
├── generate_tree.py        # Generador de árbol de directorios
├── directory_tree.txt      # Versión en texto de la estructura
├── directory_tree.png      # Versión visual
└── ...                     # Otras herramientas de desarrollo
```

- Archivos Raíz: `main.py` (inicio), `requirements.txt`, `README.md`, etc. Para ver la estructura completa, consulta `development/directory_tree.txt`.

## Cómo Ejecutar

Para iniciar el programa principal:

```
python main.py
```

Para ejecutar el descargador de cartas:

```
python development/fetch_card/fetch_card_gui.py
```

Esta herramienta accede a la API del TCG de Pokémon y guarda datos en `card_assets/cards.json` e imágenes.

## Contexto de Desarrollo y Licencia

**Contexto**: Pyokemon TCG fue creado como ejercicio didáctico y proyecto de graduación durante unas 10 semanas. El objetivo era explorar la construcción de un juego en Python con fines no comerciales. Incluye arquitectura MVC, código modular, uso de API y almacenamiento SQLite — ideal como referencia de aprendizaje. Durante el desarrollo se realizaron refactorizaciones para mejorar rendimiento y mantenimiento, incluyendo la integración de `pygame-gui` y `pygame-cards`, además de herramientas de desarrollo. El resultado es un prototipo jugable y una bitácora del aprendizaje del desarrollador. Excelente ejemplo para interesados en Python y videojuegos.

**Licencia y Descargo de Responsabilidad**: Este es un proyecto de código abierto y no comercial, creado solo con fines educativos y de entretenimiento personal. Todas las imágenes, nombres y materiales relacionados con Pokémon pertenecen a Nintendo, The Pokémon Company y sus respectivos propietarios. Este proyecto imita estos recursos solo con fines didácticos, sin infringir ni lucrar. No uses este proyecto para fines comerciales ni redistribución no autorizada. En resumen, Pyokemon TCG es solo para aprendizaje — se prohíbe su uso comercial. Se permite estudiar y referenciar el código con atribución adecuada y uso legal.

Este proyecto no incluye una licencia formal y se considera de uso educativo. Puedes modificar o extender el código bajo los principios anteriores. El autor no proporciona soporte comercial ni garantías. Las imágenes y datos de Pokémon se usan solo con fines prácticos; todos los derechos pertenecen a sus dueños originales.
