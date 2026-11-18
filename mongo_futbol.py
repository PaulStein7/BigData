from pymongo import MongoClient
import csv

URI = "mongodb+srv://pauljhan2003_db_user:***@futbolcluster.tyfgflg.mongodb.net/FutbolDB?retryWrites=true&w=majority"
client = MongoClient(URI)
db = client["FutbolDB"]
partidos = db["partidos"]
equipos = db["equipos"]

partidos.delete_many({})
equipos.delete_many({})
print("=== Conectado a MongoDB Atlas (FutbolDB) ===\n")

# ---------- CREATE (inserción desde results.csv) ----------
docs = []
nombres = set()
with open("results.csv", encoding="utf-8") as f:
    for i, fila in enumerate(csv.DictReader(f)):
        if i >= 150: break
        local, visit = int(fila["home_score"]), int(fila["away_score"])
        ganador = "local" if local > visit else ("visitante" if visit > local else "empate")
        nombres.add(fila["home_team"]); nombres.add(fila["away_team"])
        docs.append({
            "fecha": fila["date"], "equipo_local": fila["home_team"],
            "equipo_visitante": fila["away_team"],
            "marcador": {"local": local, "visitante": visit},
            "torneo": fila["tournament"],
            "sede": {"ciudad": fila["city"], "pais": fila["country"]},
            "id_partido": int(fila["id"]),
            "total_goles": local + visit, "ganador": ganador
        })

partidos.insert_many(docs)
equipos.insert_many([{"nombre": n, "tipo": "seleccion"} for n in sorted(nombres)])
print(f"✅ CREATE: {partidos.count_documents({})} partidos y {equipos.count_documents({})} equipos insertados.\n")

# ---------- READ (selección) ----------
print("--- READ: Partidos amistosos (Friendly) ---")
for p in partidos.find({"torneo": "Friendly"}).limit(3):
    print(f"  {p['fecha']} | {p['equipo_local']} {p['marcador']['local']}-{p['marcador']['visitante']} {p['equipo_visitante']}")

# ---------- UPDATE ----------
r = partidos.update_one({"id_partido": docs[0]["id_partido"]}, {"$set": {"destacado": True, "nota": "Partido histórico"}})
print(f"\n✅ UPDATE: {r.modified_count} documento marcado como destacado.")

# ---------- DELETE ----------
partidos.insert_one({"fecha": "2099-01-01", "equipo_local": "Prueba", "equipo_visitante": "Prueba",
                     "marcador": {"local": 0, "visitante": 0}, "torneo": "Prueba",
                     "sede": {"ciudad": "N/A", "pais": "N/A"}, "id_partido": 999999,
                     "total_goles": 0, "ganador": "empate"})
partidos.delete_one({"id_partido": 999999})
print("🗑️ DELETE: Documento de prueba insertado y eliminado.")

# ---------- FILTROS CON OPERADORES ----------
print("\n--- FILTRO $gt: partidos con más de 4 goles ---")
for p in partidos.find({"total_goles": {"$gt": 4}}).limit(4):
    print(f"  {p['equipo_local']} {p['marcador']['local']}-{p['marcador']['visitante']} {p['equipo_visitante']} ({p['total_goles']} goles)")

print("\n--- FILTRO $in + $and: empates en torneos específicos ---")
q = {"$and": [{"torneo": {"$in": ["FIFA World Cup", "UEFA Euro", "Copa América", "Friendly"]}}, {"ganador": "empate"}]}
for p in partidos.find(q).limit(4):
    print(f"  [{p['torneo']}] {p['equipo_local']} {p['marcador']['local']}-{p['marcador']['visitante']} {p['equipo_visitante']}")

# ---------- JOIN ($lookup) ----------
print("\n--- $lookup (join): partidos con info del equipo local ---")
pipe_l = [
    {"$limit": 3},
    {"$lookup": {"from": "equipos", "localField": "equipo_local", "foreignField": "nombre", "as": "info_local"}},
    {"$project": {"fecha": 1, "equipo_local": 1, "marcador": 1, "tipo_equipo": {"$arrayElemAt": ["$info_local.tipo", 0]}}}
]
for p in partidos.aggregate(pipe_l):
    print(f"  {p['equipo_local']} ({p.get('tipo_equipo')}) | {p['marcador']['local']}-{p['marcador']['visitante']} | {p['fecha']}")

# ---------- AGREGACIONES ----------
print("\n--- AGREGACIÓN: promedio de goles y conteo por torneo (Top 5) ---")
for r in partidos.aggregate([
    {"$group": {"_id": "$torneo", "promedio_goles": {"$avg": "$total_goles"}, "total_partidos": {"$sum": 1}}},
    {"$sort": {"total_partidos": -1}}, {"$limit": 5}]):
    print(f"  {r['_id']}: {r['promedio_goles']:.2f} goles/promedio | {r['total_partidos']} partidos")

print("\n--- AGREGACIÓN: conteo por tipo de resultado ---")
for r in partidos.aggregate([{"$group": {"_id": "$ganador", "cantidad": {"$sum": 1}}}, {"$sort": {"cantidad": -1}}]):
    print(f"  {r['_id']}: {r['cantidad']} partidos")

print("\n--- AGREGACIÓN: suma total de goles ---")
for r in partidos.aggregate([{"$group": {"_id": None, "suma_goles": {"$sum": "$total_goles"}}}]):
    print(f"  Suma total de goles: {r['suma_goles']}")

print(f"\n📈 Total de documentos: {partidos.count_documents({})}")
client.close()
print("✅ Script completado exitosamente.")