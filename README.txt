# Tarea 4 – Almacenamiento y Consultas de Datos en Big Data

**Estudiante:** Jhan Paul Zuluaga  
**Código:** 202016911A  
**Curso:** Big Data (202016911A_2204) – UNAD  
**Tutor:** Primo Martín Pino Jiménez

## Descripción

Implementación de una base de datos NoSQL en **MongoDB Atlas** para el caso de uso
"Sistema de Gestión de Partidos de Fútbol Internacional", construido sobre el
dataset `results.csv` (continuidad con la Tarea 3). Se demuestra el modelo
documental mediante subdocumentos (marcador y sede), campos opcionales y
consultas avanzadas.

## Contenido del repositorio

| Archivo | Descripción |
|---|---|
| `mongo_futbol.py` | Script principal: CRUD, filtros (`$gt`, `$in`, `$and`), join (`$lookup`) y agregaciones (`$group`, `$avg`, `$sum`, `$sort`) con PyMongo. |
| `results.csv` | Dataset de partidos internacionales de fútbol (1872–2023). |

## Diseño de la base de datos

- **Base de datos:** `FutbolDB` (clúster `FutbolCluster`, MongoDB Atlas 8.0)
- **Colección `partidos`:** fecha, equipo_local, equipo_visitante, marcador {local, visitante}, torneo, sede {ciudad, pais}, id_partido, total_goles, ganador, destacado (opcional).
- **Colección `equipos`:** nombre, tipo. Usada para demostrar joins con `$lookup`.

## Requisitos

- Python 3.11 o superior
- Librería PyMongo: `pip install pymongo`
- Cuenta en MongoDB Atlas con clúster activo y acceso de red configurado (0.0.0.0/0)

## Ejecución

1. Configurar la cadena de conexión como variable de entorno (por seguridad, la contraseña no está en el código):

   ```bash
   export MONGO_URI="mongodb+srv://usuario:contraseña@futbolcluster.tyfgflg.mongodb.net/FutbolDB?retryWrites=true&w=majority"