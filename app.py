import streamlit as st
import pandas as pd
import os

from datetime import datetime
FECHA_LIMITE = datetime(2026, 5, 30, 10, 0, 0)

def obtener_resultado(goles_a, goles_b):

    if goles_a > goles_b:
        return "A"

    elif goles_b > goles_a:
        return "B"

    else:
        return "EMPATE"


def calcular_puntos(
    pred_a,
    pred_b,
    real_a,
    real_b
):

    puntos = 0

    resultado_pred = obtener_resultado(pred_a, pred_b)
    resultado_real = obtener_resultado(real_a, real_b)

    # Acertó ganador/empate
    if resultado_pred == resultado_real:
        puntos += 1

    # Acertó marcador exacto
    if pred_a == real_a and pred_b == real_b:
        puntos += 1

    return puntos

ARCHIVO_PRONOSTICOS = "pronosticos.csv"

st.title("Mundialito ICCA")

st.write("Pronósticos de la fase de grupos")

st.divider()

ahora = datetime.now()

if ahora > FECHA_LIMITE:
    st.error("El plazo para ingresar pronósticos ha finalizado.")
    st.stop()
else:
    st.info(f"Puedes ingresar pronósticos hasta: {FECHA_LIMITE.strftime('%d/%m/%Y %H:%M')}")


nombre = st.text_input("Nombre del participante")

# Leer partidos desde CSV
df_partidos = pd.read_csv("partidos.csv", encoding="latin1", sep=";")

if os.path.exists("resultados.csv"):
    df_resultados = pd.read_csv(
        "resultados.csv",
        encoding="latin1",
        sep=";"
    )
else:
    df_resultados = None

pronosticos = []

# Crear formulario para cada partido
# Crear formulario para cada partido
for _, partido in df_partidos.iterrows():

    equipo_a = partido["equipo_a"]
    equipo_b = partido["equipo_b"]

    st.subheader(f"{equipo_a} vs {equipo_b}")

    col1, col2 = st.columns(2)

    with col1:
        goles_a = st.number_input(
            f"Goles de {equipo_a}",
            min_value=0,
            max_value=20,
            step=1,
            key=f"goles_a_{partido['id_partido']}"
        )

    with col2:
        goles_b = st.number_input(
            f"Goles de {equipo_b}",
            min_value=0,
            max_value=20,
            step=1,
            key=f"goles_b_{partido['id_partido']}"
        )

    pronosticos.append({
        "id_partido": partido["id_partido"],
        "equipo_a": equipo_a,
        "equipo_b": equipo_b,
        "goles_a": goles_a,
        "goles_b": goles_b
    })

st.divider()

if st.button("Guardar todos los pronósticos"):

    if nombre.strip() == "":
        st.error("Debes escribir tu nombre.")

    else:

        registros = []

        for p in pronosticos:

            registros.append({
                "nombre": nombre,
                "id_partido": p["id_partido"],
                "equipo_a": p["equipo_a"],
                "equipo_b": p["equipo_b"],
                "goles_a": p["goles_a"],
                "goles_b": p["goles_b"]
            })



        nuevo_df = pd.DataFrame(registros)

        if os.path.exists(ARCHIVO_PRONOSTICOS):

            df_existente = pd.read_csv(ARCHIVO_PRONOSTICOS)

            df_final = pd.concat(
                [df_existente, nuevo_df],
                ignore_index=True
            )

        else:
            df_final = nuevo_df

        df_final.to_csv(ARCHIVO_PRONOSTICOS, index=False)

        st.success("Pronósticos guardados correctamente.")

st.divider()

st.subheader("Pronósticos registrados")

if os.path.exists(ARCHIVO_PRONOSTICOS):

    df = pd.read_csv(ARCHIVO_PRONOSTICOS)

    st.dataframe(df)

else:
    st.info("Todavía no existen pronósticos.")

    st.divider()

st.header("Tabla de posiciones")

if (
    os.path.exists("pronosticos.csv")
    and os.path.exists("resultados.csv")
):

    df_pronosticos = pd.read_csv(
        "pronosticos.csv"
    )

    df_resultados = pd.read_csv(
        "resultados.csv",
        encoding="latin1",
        sep=";"
    )

    df = df_pronosticos.merge(
        df_resultados,
        on="id_partido",
        how="inner"
    )

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

    if len(ranking) > 0:

        df_ranking = pd.DataFrame(ranking)

        tabla = df_ranking.groupby(
            "nombre"
        )["puntos"].sum().reset_index()

        tabla = tabla.sort_values(
            by="puntos",
            ascending=False
        )

        st.dataframe(tabla)

    else:
        st.info(
            "No hay coincidencias entre pronósticos y resultados."
        )

else:
    st.info(
        "Faltan resultados o pronósticos."
    )
    
if os.path.exists("pronosticos.csv"):

    df_pronosticos = pd.read_csv(
        "pronosticos.csv"
    )

    csv = df_pronosticos.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Descargar pronósticos",
        data=csv,
        file_name="pronosticos.csv",
        mime="text/csv"
    )
  