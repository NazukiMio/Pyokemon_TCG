# Pyokemon TCG – Descripción del Proyecto (Python/PyGame)

(Consulta la versión en inglés de este README [aquí](README_EN.md). También está disponible una versión en chino [aquí](README_CN.md).)

## Introducción

**Pyokemon TCG** es un simulador educativo del juego de cartas coleccionables de Pokémon, desarrollado en Python usando PyGame. Este proyecto no es oficial y no tiene fines comerciales; su objetivo es recrear la dinámica del Pokémon TCG en un entorno digital para fines didácticos. Pyokemon TCG sirve como ejercicio práctico y material de aprendizaje, mostrando cómo construir un videojuego estructurado en Python con gestión de estados, interfaz gráfica interactiva y conexión a APIs públicas. El énfasis está en la claridad del código y la arquitectura modular, lo que permite estudiar y entender fácilmente sus componentes. En resumen, es un prototipo jugable diseñado para aprender sobre desarrollo de juegos (más que para su distribución comercial), combinando diversión y educación en un mismo proyecto.

## Resumen de Funcionalidades

- **Registro y Autenticación de Usuario**: El juego cuenta con un sistema de usuarios que permite crear un perfil nuevo o iniciar sesión con un perfil existente. Los datos de perfil y progreso se guardan localmente en una base de datos SQLite. Durante el inicio de sesión, un gestor de autenticación verifica las credenciales y mantiene la sesión activa de forma segura (sin exponer identificadores sensibles entre pantallas).

- **Sistema de Cartas – “Pokédex”**: Incluye una Pokédex o colección de cartas donde el usuario puede visualizar todas las cartas de Pokémon TCG disponibles en el juego, y ver cuáles ha conseguido. La colección se presenta en formato gráfico con miniaturas de las cartas, usando un sistema de caché de imágenes para optimizar el rendimiento. El usuario puede filtrar las cartas por criterios (todas, en posesión, faltantes; por rareza; por tipo, etc.) para explorar fácilmente su colección.

- **Navegación entre Pantallas**: Una barra de navegación modular permite moverse entre las distintas secciones del juego de manera fluida. Por ejemplo, el jugador puede pasar de la pantalla principal a la Pokédex, de allí a la tienda, o a la preparación de combate con un simple clic. Las transiciones están animadas suavemente gracias a `pygame-gui`, proporcionando una experiencia de usuario agradable y una estructura interna organizada en escenas.

- **Compra y Apertura de Sobres**: El juego simula la adquisición de cartas nuevas mediante sobres (boosters). En la tienda se pueden “comprar” sobres usando la moneda virtual del juego, y luego abrirlos en una interfaz dedicada. Al abrir un sobre, se muestra una animación donde el paquete se abre y revela las cartas aleatorias que contiene, recreando la emoción del TCG real. Esta funcionalidad ya está implementada con un sistema gráfico interactivo integrado en una ventana modal de tienda, incluyendo efectos visuales y distribución de rarezas similar a la real.

- **Persistencia de Datos Local**: Todo el progreso se almacena de forma local. Se utiliza SQLite para guardar perfiles de usuario, cartas obtenidas, mazos creados, logros, economía del juego, etc. Esto permite que el juego funcione completamente offline una vez inicializado (solo se requiere conexión a internet para descargar datos la primera vez si se usa la herramienta de importación). La elección de SQLite simplifica la instalación (no se requiere configurar servidor) y es suficiente para manejar los datos de un solo jugador.

- **Herramienta Externa de Importación de Cartas**: Para poblar el juego con datos de cartas reales, se desarrolló una herramienta llamada `fetch_card_gui` (con interfaz gráfica usando Tkinter). Esta utilidad permite descargar desde la API pública de Pokémon TCG un conjunto de cartas y sus imágenes, según parámetros configurables (por ejemplo, cuántas cartas de cada rareza). La herramienta guarda los datos en un archivo JSON (`cards.json`) y las imágenes correspondientes, que el juego luego integra a su base de datos local.

- **Editor de Mazos (en desarrollo)**: Una funcionalidad prevista es un editor donde el jugador pueda armar sus propios mazos seleccionando cartas de su colección. El mazo personalizado se podrá guardar y luego usar en combates. Si bien la estructura básica está diseñada (e incluso hay código parcial bajo `game/scenes/windows/deck_builder/`), esta característica está en fase de desarrollo y puede no estar completamente operativa en la versión actual.

- **Sistema de Combate Local (en desarrollo)**: Se está implementando un sistema de combate por turnos para partidas individuales contra la IA. El backend de la lógica de combate por turnos ya está funcional, y actualmente se integra con una interfaz gráfica de batalla usando `pygame-cards` para mostrar cartas y `pygame-gui` para los controles. Esto permitirá que el jugador se enfrente a un oponente controlado por el ordenador en duelos 1v1.

- **Más en el Horizonte**: El proyecto contempla posibles expansiones a largo plazo gracias a su arquitectura extensible. Por ejemplo, se planifica una tienda más amplia con ítems u objetos desbloqueables, un sistema de logros y misiones, y eventualmente características en línea (multijugador, intercambio de cartas, etc.). Actualmente estos elementos no están operativos, pero algunas bases (como la estructura para enviar y recibir datos online) están esbozadas en el código esperando implementaciones futuras.

## Instalación y Dependencias

**Requisitos**: Python 3.10 o superior. Recomendado usar entorno virtual.

Instalar dependencias:

```
pip install -r requirements.txt
```

**Dependencias principales**:

- `pygame` – motor de renderizado y bucle principal
- `pygame-gui` – interfaz gráfica moderna
- `pygame-cards` – soporte visual para cartas (en combate)
- `requests` – llamadas a la API externa
- `Pillow` – procesamiento de imágenes
- `sqlite3` – base de datos local (integrado en Python)
- `tkinter` – GUI de la herramienta de importación (integrado en Python)
- `opencv-python`, `graphviz`, `tqdm` – para herramientas de desarrollo

Asegúrate de tener un entorno con soporte gráfico (PyGame abre una ventana). No se necesita configuración especial en Windows, Mac o Linux más allá de instalar los paquetes.

## Cómo Ejecutar

Lanzar el juego:

```
python main.py
```

Lanzar la herramienta de importación:

```
python development/fetch_card/fetch_card_gui.py
```

Esto abrirá la GUI para descargar cartas desde la API y guardarlas localmente.

## Estructura del Proyecto

```
├── main.py
├── requirements.txt
├── README_ES.md
├── game/
│   ├── core/         # lógica central, autenticación, base de datos
│   ├── scenes/       # pantallas: login, home, pokedex, batalla...
│   ├── ui/           # elementos de interfaz reutilizables
│   └── utils/        # utilidades generales
├── assets/           # imágenes, sonidos, fuentes
├── data/             # base de datos SQLite, archivos JSON
├── development/
│   ├── fetch_card/   # herramienta externa para importar cartas
│   ├── generate_tree.py
├── docs/             # documentación adicional
```

## Contexto y Licencia

**Pyokemon TCG** fue desarrollado como proyecto académico con fines educativos. No está afiliado con Nintendo ni The Pokémon Company. Todos los elementos relacionados con Pokémon se utilizan bajo términos de “uso justo” para fines no comerciales.

**Licencia**: Código abierto para uso personal y educativo. **Queda prohibido el uso comercial o redistribución sin autorización**.

---

¡Diviértete programando y explorando el mundo del TCG de Pokémon con este proyecto en Python!
