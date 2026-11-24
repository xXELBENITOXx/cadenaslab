# CadenasLab — Laboratorio de similitud textual

Proyecto académico interactivo sobre **herramientas de análisis de cadenas y teoría de números**. Compara **dos textos que introduce la persona usuaria** mediante ventanas de palabras y *rolling hash* polinómico (Rabin–Karp), con verificación de palabras para descartar colisiones de hash. También incluye un laboratorio de **KMP, Boyer–Moore–Horspool, algoritmo de Euclides, exponenciación modular y criba de Eratóstenes**.

> **Importante:** CadenasLab **no es un detector de plagio concluyente**. El porcentaje expresa coincidencia literal entre los dos documentos suministrados. No busca en Internet, no comprueba citas ni determina autoría.

## Funciones reales

- Comparador de dos textos (hasta 20.000 caracteres por cuadro).
- Normalización de mayúsculas y tildes para la comparación (sin modificar los textos mostrados).
- Ventanas de hasta 5 palabras con hash polinómico y **módulo primo 1.000.000.007**.
- Coincidencias resaltadas en ambos textos, porcentaje y fragmentos comunes.
- Laboratorio interactivo que ejecuta algoritmos de **Python**, no simulaciones numéricas del navegador.
- Reporte descargable `.txt`.
- Historial optativo: guarda **solo métricas anónimas**, no el contenido de los textos.
- Interfaz adaptable a ordenador y teléfono.

## Arquitectura

```text
Navegador (HTML, CSS, JavaScript)
          |
          | HTTP /api/analyze, /api/algorithm, /api/history
          v
Motor Python (src/analysis.py)
          |
          v
Cloudflare Python Worker (src/entry.py)
          |
          v
Cloudflare D1 (tabla analyses, solo estadísticas)
```

En **desarrollo local**, `src/local_server.py` ejecuta la misma lógica Python con SQLite para que se pueda demostrar incluso sin Cloudflare.

## 1. Probar ahora en tu ordenador (la forma más fácil)

Necesitas **Python 3.12+** y no hace falta instalar librerías.

```bash
cd cadenaslab
python src/local_server.py
```

Abre `http://localhost:8765` en Chrome. Pulsa **Cargar ejemplo** y luego **Analizar textos**. Marca **Guardar métricas en historial** solo si deseas crear un registro en la base local.

Para detenerlo, pulsa `Ctrl+C` en la consola.

La base local se guarda en `.local/cadenaslab.sqlite3` (no se sube al repositorio).

## 2. Crear el repositorio de GitHub

1. En GitHub, crea un repositorio vacío llamado `cadenaslab` (no marques README si vas a subir estos archivos).
2. Descomprime el archivo ZIP y abre una terminal en la carpeta `cadenaslab`.
3. Sustituye `TU_USUARIO` por tu usuario de GitHub:

```bash
git init
git add .
git commit -m "Proyecto académico CadenasLab"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/cadenaslab.git
git push -u origin main
```

Si GitHub solicita inicio de sesión, autoriza tu cuenta o utiliza GitHub Desktop. **Este paquete no crea automáticamente el repositorio en tu cuenta.**

## 3. Crear Cloudflare D1

Necesitas Node.js, `npm`, una cuenta de Cloudflare y, para la ruta Python recomendada, [`uv`](https://docs.astral.sh/uv/).

Instala dependencias de desarrollo:

```bash
npm install
uv sync
```

Inicia sesión:

```bash
npx wrangler login
```

Crea una base **nueva**, independiente de la de Aura Parfum:

```bash
npx wrangler d1 create cadenaslab-db
```

La consola mostrará un `database_id` tipo UUID. Cópialo en `wrangler.jsonc` reemplazando `REEMPLAZAR_CON_ID_D1`. El `binding` debe seguir siendo `DB`.

Crea la tabla en D1 remoto mediante la migración incluida:

```bash
npx wrangler d1 migrations apply cadenaslab-db --remote
```

En caso de solicitar confirmación, acepta. La tabla creada es `analyses`, con campos para puntuación, número de palabras, coincidencias y fecha.

## 4. Publicar el Worker en Cloudflare

Con `uv` instalado y después de crear la base:

```bash
uv run pywrangler deploy
```

Como alternativa, verifica si tu versión de Wrangler permite:

```bash
npx wrangler deploy
```

La URL de publicación tendrá el formato `https://cadenaslab.TU_SUBDOMINIO.workers.dev`. **No es una URL activa hasta que termines el despliegue**.

Para actualizar automáticamente desde GitHub: Cloudflare → **Workers & Pages** → **Create application** → **GitHub** → elige `cadenaslab` → configura el proyecto Worker con el mismo nombre y el comando de despliegue del entorno → conecta la rama `main`.

> El despliegue **no está probado en una cuenta real** y las opciones concretas de Cloudflare pueden cambiar. Es indispensable crear D1 y pegar el ID real antes de desplegar. Consulta las referencias oficiales al final.

## 5. Pruebas

```bash
python -m unittest discover -s tests -v
```

Hay 11 pruebas automáticas para similitud, mayúsculas y tildes, coincidencias parciales, tamaños máximos, KMP, Boyer–Moore–Horspool, Euclides, módulo y números primos.

## Algoritmo principal: cómo explicarlo

1. **Tokenización:** separa ambos textos en palabras y recuerda sus posiciones.
2. **Normalización:** usa minúsculas y quita tildes solo para comparar.
3. **Shingling:** crea ventanas de 5 palabras (o de 3–4 si ambos textos son breves).
4. **Rabin–Karp:** calcula un hash rodante con base `911382323` y módulo primo `1000000007`.
5. **Verificación exacta:** compara la secuencia real de palabras para descartar colisiones.
6. **Cobertura:** cuenta qué porcentaje de palabras en cada texto pertenece a alguna ventana coincidente.
7. **Puntuación:** `similitud = (cobertura_A + cobertura_B) / 2`. Es una métrica didáctica, **no** una probabilidad de plagio.

## Privacidad y limitaciones

- Por defecto **no se guarda nada** en D1 al analizar.
- Cuando se activa «Guardar métricas», solo se almacenan **estadísticas**. El historial es **compartido** en este prototipo; no hay cuentas de usuario, permisos ni borrado individual.
- No contiene buscador web, buscador en repositorios universitarios ni análisis semántico.
- Los textos pueden contener expresiones muy comunes, citas correctamente atribuidas o fragmentos coincidentes por casualidad.
- No compara bien las paráfrasis o traducciones: busca secuencias **literales**.
- Evita pegar trabajos confidenciales en una instancia pública si no confías en quien administra el servidor.
- Este es un **prototipo académico**; antes de uso institucional se recomiendan autenticación, rate limiting y política de tratamiento de datos.

## Archivos importantes

| Archivo | Función |
|---|---|
| `public/index.html` | Estructura de todas las vistas |
| `public/style.css` | Diseño y adaptación móvil |
| `public/app.js` | Interacciones, peticiones al servidor y resaltado |
| `src/analysis.py` | Algoritmos implementados en Python |
| `src/entry.py` | Servidor Cloudflare Workers y enlace D1 |
| `src/local_server.py` | Servidor local Python + SQLite |
| `migrations/0001_init.sql` | Estructura de la base de datos |
| `wrangler.jsonc` | Configuración de Cloudflare |
| `tests/test_analysis.py` | Pruebas automáticas |
| `previews/*.png` | Vistas previas del diseño |
| `docs/GUIA_EXPOSICION.md` | Guion para tres integrantes |

## Referencias verificadas (23 de noviembre de 2026)

- Cloudflare Python Workers: https://developers.cloudflare.com/workers/languages/python/
- Python Workers + D1: https://developers.cloudflare.com/d1/examples/query-d1-from-python-workers/
- Cloudflare Workers Git integration: https://developers.cloudflare.com/workers/ci-cd/builds/
- Cloudflare D1 migraciones: https://developers.cloudflare.com/d1/reference/migrations/
- Cloudflare Workers estáticos: https://developers.cloudflare.com/workers/static-assets/

