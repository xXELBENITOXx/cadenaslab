"""Cloudflare Python Worker: API y D1 para CadenasLab."""
from urllib.parse import urlparse
from workers import WorkerEntrypoint, Response
from analysis import analyze, algorithm, MAX_CHARS


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        path = urlparse(request.url).path
        method = request.method.upper()
        try:
            if path == "/api/health" and method == "GET":
                return Response.json({"ok": True, "engine": "Python", "database": "D1"})
            if path == "/api/analyze" and method == "POST":
                body = await request.json()
                text_a = body.get("text_a", "")
                text_b = body.get("text_b", "")
                result = analyze(text_a, text_b)
                if body.get("save"):
                    # No se guardan textos originales: solo estadísticas anónimas.
                    await self.env.DB.prepare(
                        "INSERT INTO analyses (score, words_a, words_b, matched_a, matched_b, window_size) VALUES (?, ?, ?, ?, ?, ?)"
                    ).bind(result["score"], result["words_a"], result["words_b"],
                           result["matched_words_a"], result["matched_words_b"], result["window"]).run()
                    result["saved"] = True
                else:
                    result["saved"] = False
                return Response.json(result)
            if path == "/api/algorithm" and method == "POST":
                body = await request.json()
                return Response.json(algorithm(body))
            if path == "/api/history" and method == "GET":
                response = await self.env.DB.prepare(
                    "SELECT id, score, words_a, words_b, matched_a, matched_b, window_size, created_at "
                    "FROM analyses ORDER BY id DESC LIMIT 25"
                ).all()
                return Response.json({"items": response.results.to_py()})
            if path.startswith("/api/"):
                return Response.json({"error": "Ruta no encontrada."}, status=404)
            return await self.env.ASSETS.fetch(request)
        except (ValueError, TypeError) as exc:
            return Response.json({"error": str(exc)}, status=400)
        except Exception:
            return Response.json({"error": "No fue posible procesar la solicitud. Verifica D1 y la migración."}, status=500)
