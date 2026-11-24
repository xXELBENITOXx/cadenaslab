# Guía de presentación: CadenasLab

**Título del proyecto:** CadenasLab: análisis de cadenas y teoría de números aplicado a la comparación de textos.

**Objetivo:** demostrar con una aplicación web cómo los algoritmos de procesamiento de cadenas y los residuos modulares permiten encontrar coincidencias textuales.

**Duración sugerida:** entre 9 y 12 minutos. **Integrantes:** 3. Reparto equilibrado.

## Integrante 1 — Problema, diseño y uso (3–4 min)

> «Nuestro tema es Herramientas de análisis de cadenas y Teoría de Números. En lugar de limitar la exposición a definiciones, construimos una aplicación web llamada CadenasLab. Su función principal es comparar dos textos y resaltar fragmentos escritos de forma similar. No decide si hubo plagio, porque esa valoración necesita contexto, fuentes y revisión humana. Sí nos ayuda a observar cómo funcionan los algoritmos que estamos estudiando.»

**Demostración:** en el menú Analizador, pulsa **Cargar ejemplo**, señala los dos documentos y pulsa **Analizar textos**. Muestra el porcentaje resultante, los fragmentos amarillos y la cobertura de ambos documentos. Explica que dos documentos iguales dan cerca de 100 % y documentos sin ventanas comunes dan 0 %.

**Qué indicar del código:** `public/index.html` contiene las secciones visibles, `style.css` los colores y disposición, `app.js` envía los textos al motor Python mediante `fetch('/api/analyze', ...)`.

## Integrante 2 — Análisis de cadenas: Rabin–Karp, KMP y Boyer–Moore (3–4 min)

> «El motor principal divide los textos en palabras, las normaliza y crea ventanas de cinco palabras. Cada ventana se transforma en un valor numérico mediante un hash polinómico, usando un número primo como módulo. Ese método está inspirado en Rabin–Karp. Una igualdad de hash es una candidata: por eso verificamos que las palabras coincidan de verdad.»

**Ejemplo rápido:** dos textos contienen la frase «los algoritmos de búsqueda de cadenas permiten». En ambos aparece el mismo segmento de palabras y la página lo destaca. Si solo coincide una palabra suelta, no se marca como bloque de cinco.

**Demostración:** entra en Laboratorio de algoritmos y ejecuta **KMP** con texto `ABABCABABC` y patrón `ABC`. Muestra posiciones **2** y **7**. Indica que KMP usa una tabla LPS para evitar repetir comparaciones. Cambia a **Boyer–Moore**; muestra que la versión Horspool realiza saltos de posiciones según la última letra de la ventana.

**Código para mostrar:** `src/analysis.py`, funciones `rolling_hashes()`, `analyze()`, `kmp_search()` y `boyer_moore_horspool()`.

## Integrante 3 — Teoría de números, base de datos y cierre (3–4 min)

> «La teoría de números aparece en el algoritmo principal porque calculamos residuos con un módulo primo de 1.000.000.007. Además, incorporamos herramientas de Euclides, exponenciación modular y números primos, todas ejecutadas en Python. Es una conexión práctica entre matemáticas e Ingeniería de Sistemas.»

**Demostración:** ejecuta **Euclides** con 48 y 18: residuos 12, 6, 0, y MCD = 6. Luego ejecuta exponenciación modular con base 3, exponente 7 y módulo 11: 3⁷ mod 11 = **9**. En la criba, muestra los números primos de 2 a 60.

**Base de datos:** `migrations/0001_init.sql` crea la tabla `analyses`. `src/entry.py` se conecta con la base D1 de Cloudflare usando el binding `DB`. Marca **Guardar métricas**, compara dos textos y entra en Historial para mostrar un registro. Precisa que solamente se guardan valores numéricos, no los escritos.

**Cierre sugerido:** «Con CadenasLab comprobamos que algoritmos como Rabin–Karp, KMP y Euclides no son solo teoría: pueden implementarse y servir para analizar información y desarrollar software. Nuestro prototipo es educativo y todavía no compara documentos de Internet ni permite afirmar plagio.»

## Preguntas que podría hacer el docente

**¿Es un detector de plagio real?** Es un prototipo de detección de coincidencias literales **entre dos documentos proporcionados**. No realiza búsqueda mundial ni evaluación jurídica/académica de plagio.

**¿Qué es una cadena?** Una sucesión ordenada de caracteres, por ejemplo `"ABABCABABC"`.

**¿Qué significa Rabin–Karp?** Es un método de búsqueda que usa hashes y una ventana deslizante. En el prototipo lo adaptamos a secuencias de palabras.

**¿Por qué usar un número primo?** Para el cálculo del hash modular, donde se reducen los valores numéricos mediante residuos. No garantiza ausencia de colisiones, por eso hay verificación exacta.

**¿Cómo sale el porcentaje?** Se promedia el porcentaje de palabras que pertenecen a bloques coincidentes en el texto A y en el texto B. No es una estimación estadística de probabilidad de fraude.

**¿Por qué Python?** Permite implementar los algoritmos de forma legible y tiene soporte en Cloudflare Workers. El navegador usa JavaScript solo para la interfaz.

**¿Para qué sirve D1?** Para registrar fecha, porcentaje y número de palabras cuando el usuario lo solicita. No guarda los textos originales.

**¿Qué diferencia hay entre KMP y Boyer–Moore?** KMP usa información de prefijos del patrón para evitar retrocesos; Boyer–Moore–Horspool aprovecha saltos basados en caracteres al comparar desde la derecha.

**¿Qué limitación importante tiene?** No reconoce paráfrasis, citas ni coincidencias con documentos que no le hayan proporcionado; tampoco determina plagio.

## Ensayo en clase: 6 clics

1. Abre `http://localhost:8765` si presentas desde tu equipo.
2. Pulsa **Cargar ejemplo** → **Analizar textos** y señala el resultado de **59,0 %**.
3. Selecciona **Laboratorio de algoritmos** → ejecuta **KMP**.
4. Abre **Euclides** → ejecuta **48 y 18**.
5. Abre **Criba de Eratóstenes** → pulsa ejecutar.
6. Opcional: guarda métricas desde el comparador y abre **Historial**.

> El 59,0 % corresponde exclusivamente a los dos textos de ejemplo incluidos en esta versión. Si cambian los textos o el algoritmo, cambia el porcentaje.
