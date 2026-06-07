import streamlit as st
import pandas as pd
import os
import re
from io import StringIO


ARCHIVO_PRONOSTICOS = "pronosticos.csv"
ARCHIVO_RESULTADOS = "resultados.csv"


def obtener_resultado(goles_a, goles_b):
    if goles_a > goles_b:
        return "A"
    elif goles_b > goles_a:
        return "B"
    else:
        return "EMPATE"


def calcular_puntos(pred_a, pred_b, real_a, real_b):
    puntos = 0

    if obtener_resultado(pred_a, pred_b) == obtener_resultado(real_a, real_b):
        puntos += 1

    if pred_a == real_a and pred_b == real_b:
        puntos += 1

    return puntos


def limpiar_csv(df):
    df.columns = [
        re.sub(r";+$", "", str(c).strip())
        for c in df.columns
    ]

    for col in df.columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
            .str.replace(r";+$", "", regex=True)
        )

    return df


def leer_archivo_texto(archivo):
    try:
        with open(archivo, "r", encoding="utf-8-sig") as f:
            return f.read()
    except UnicodeDecodeError:
        with open(archivo, "r", encoding="latin1") as f:
            return f.read()


def leer_pronosticos_limpios(archivo):
    texto = leer_archivo_texto(archivo)

    # Elimina punto y coma sobrantes al final de cada línea.
    texto = re.sub(r";+\s*$", "", texto, flags=re.MULTILINE)

    df = pd.read_csv(
        StringIO(texto),
        sep=",",
        dtype=str
    )

    df = limpiar_csv(df)

    columnas_esperadas = [
        "registro",
        "nombre",
        "id_partido",
        "equipo_a",
        "equipo_b",
        "goles_a",
        "goles_b"
    ]

    # Si la cabecera quedó corrida, reconstruimos el archivo.
    if "id_partido" not in df.columns or "goles_b" not in df.columns:
        df = pd.read_csv(
            StringIO(texto),
            sep=",",
            dtype=str,
            header=None,
            skiprows=1,
            names=columnas_esperadas
        )
        df = limpiar_csv(df)

    return df


def leer_resultados_limpios(archivo):
    texto = leer_archivo_texto(archivo)

    texto = re.sub(r";+\s*$", "", texto, flags=re.MULTILINE)

    df = pd.read_csv(
        StringIO(texto),
        sep=",",
        dtype=str
    )

    df = limpiar_csv(df)

    return df


def convertir_a_entero(df, columnas):
    for columna in columnas:
        df[columna] = pd.to_numeric(
            df[columna],
            errors="coerce"
        )

    filas_invalidas = df[df[columnas].isna().any(axis=1)]

    if not filas_invalidas.empty:
        st.error(
            "Hay filas con datos no numéricos en columnas que deberían ser números."
        )
        st.dataframe(filas_invalidas)
        st.stop()

    for columna in columnas:
        df[columna] = df[columna].astype(int)

    return df


st.title("Mundialito ICCA")
st.write("Pronósticos registrados y ranking de participantes")

st.divider()

st.subheader("Pronósticos registrados")

if not os.path.exists(ARCHIVO_PRONOSTICOS):
    st.warning("Todavía no existe pronosticos.csv.")
    st.stop()


df_pronosticos = leer_pronosticos_limpios(ARCHIVO_PRONOSTICOS)

columnas_pronosticos = [
    "nombre",
    "id_partido",
    "grupo",
    "equipo_a",
    "equipo_b",
    "goles_a",
    "goles_b"
]

faltantes_pronosticos = [
    columna
    for columna in columnas_pronosticos
    if columna not in df_pronosticos.columns
]

if faltantes_pronosticos:
    st.error(
        f"Faltan columnas en pronosticos.csv: {faltantes_pronosticos}"
    )
    st.write("Columnas detectadas:")
    st.write(list(df_pronosticos.columns))
    st.stop()


df_pronosticos = convertir_a_entero(
    df_pronosticos,
    ["id_partido", "goles_a", "goles_b"]
)

st.dataframe(df_pronosticos)

csv_pronosticos = df_pronosticos.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Descargar pronósticos limpios",
    data=csv_pronosticos,
    file_name="pronosticos_limpios.csv",
    mime="text/csv"
)


st.divider()

st.header("Tabla de posiciones")

if not os.path.exists(ARCHIVO_RESULTADOS):
    st.info(
        "Todavía no existe resultados.csv. Cuando lo subas, se calculará el ranking."
    )
    st.stop()


df_resultados = leer_resultados_limpios(ARCHIVO_RESULTADOS)

columnas_resultados = [
    "id_partido",
    "goles_real_a",
    "goles_real_b"
]

faltantes_resultados = [
    columna
    for columna in columnas_resultados
    if columna not in df_resultados.columns
]

if faltantes_resultados:
    st.error(
        f"Faltan columnas en resultados.csv: {faltantes_resultados}"
    )
    st.write("Columnas detectadas:")
    st.write(list(df_resultados.columns))
    st.stop()


df_resultados = convertir_a_entero(
    df_resultados,
    ["id_partido", "goles_real_a", "goles_real_b"]
)

df = df_pronosticos.merge(
    df_resultados,
    on="id_partido",
    how="inner"
)

if df.empty:
    st.info("No hay coincidencias entre pronósticos y resultados.")
    st.stop()


ranking = []

for _, fila in df.iterrows():
    puntos = calcular_puntos(
        fila["goles_a"],
        fila["goles_b"],
        fila["goles_real_a"],
        fila["goles_real_b"]
    )

    ranking.append({
        "nombre": fila["nombre"],
        "puntos": puntos
    })


df_ranking = pd.DataFrame(ranking)

tabla = df_ranking.groupby(
    "nombre"
)["puntos"].sum().reset_index()

tabla = tabla.sort_values(
    by="puntos",
    ascending=False
)

st.dataframe(tabla)

csv_ranking = tabla.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Descargar ranking",
    data=csv_ranking,
    file_name="ranking.csv",
    mime="text/csv"
)