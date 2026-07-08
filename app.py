import streamlit as st
import pandas as pd
import os


ARCHIVO_PARTIDOS = "partidos_cuartos.csv"
ARCHIVO_PRONOSTICOS = "pronosticos_cuartos.csv"


def leer_csv_seguro(archivo):
    try:
        return pd.read_csv(
            archivo,
            encoding="utf-8-sig",
            sep=",",
            dtype=str
        )
    except UnicodeDecodeError:
        return pd.read_csv(
            archivo,
            encoding="latin1",
            sep=",",
            dtype=str
        )


st.title("Mundialito - Cuartos de Final")
st.write("Ingreso de pronósticos de cuartos de final")

st.divider()

if not os.path.exists(ARCHIVO_PARTIDOS):
    st.error("No existe el archivo partidos_cuartos.csv.")
    st.stop()


df_partidos = leer_csv_seguro(ARCHIVO_PARTIDOS)
df_partidos.columns = df_partidos.columns.str.strip()

columnas_partidos = [
    "id_partido",
    "fase",
    "equipo_a",
    "equipo_b"
]

faltantes_partidos = [
    c for c in columnas_partidos
    if c not in df_partidos.columns
]

if faltantes_partidos:
    st.error(f"Faltan columnas en partidos_cuartos.csv: {faltantes_partidos}")
    st.stop()


df_partidos["id_partido"] = df_partidos["id_partido"].astype(int)

nombre = st.text_input("Nombre del participante")

st.divider()

pronosticos = []

for _, partido in df_partidos.iterrows():

    id_partido = int(partido["id_partido"])
    fase = partido["fase"]
    equipo_a = partido["equipo_a"]
    equipo_b = partido["equipo_b"]

    st.subheader(f"{fase}: {equipo_a} vs {equipo_b}")
    st.caption("Pronóstico del marcador en los 90 minutos reglamentarios.")

    col1, col2 = st.columns(2)

    with col1:
        goles_a = st.number_input(
            f"Goles de {equipo_a}",
            min_value=0,
            max_value=20,
            step=1,
            key=f"goles_a_{id_partido}"
        )

    with col2:
        goles_b = st.number_input(
            f"Goles de {equipo_b}",
            min_value=0,
            max_value=20,
            step=1,
            key=f"goles_b_{id_partido}"
        )

    pronosticos.append({
        "id_partido": id_partido,
        "fase": fase,
        "equipo_a": equipo_a,
        "equipo_b": equipo_b,
        "goles_a": int(goles_a),
        "goles_b": int(goles_b)
    })


st.divider()

if st.button("Guardar pronósticos de cuartos"):

    if nombre.strip() == "":
        st.error("Debes escribir tu nombre.")

    else:
        registros = []

        for p in pronosticos:
            registros.append({
                "nombre": nombre.strip(),
                "id_partido": p["id_partido"],
                "fase": p["fase"],
                "equipo_a": p["equipo_a"],
                "equipo_b": p["equipo_b"],
                "goles_a": p["goles_a"],
                "goles_b": p["goles_b"]
            })

        nuevo_df = pd.DataFrame(registros)

        if os.path.exists(ARCHIVO_PRONOSTICOS):
            df_existente = leer_csv_seguro(ARCHIVO_PRONOSTICOS)
            df_existente.columns = df_existente.columns.str.strip()

            df_final = pd.concat(
                [df_existente, nuevo_df],
                ignore_index=True
            )

        else:
            df_final = nuevo_df

        df_final.to_csv(
            ARCHIVO_PRONOSTICOS,
            index=False,
            encoding="utf-8-sig"
        )

        st.success("Pronósticos guardados correctamente.")


st.divider()

st.subheader("Pronósticos registrados")

if os.path.exists(ARCHIVO_PRONOSTICOS):

    df = leer_csv_seguro(ARCHIVO_PRONOSTICOS)
    df.columns = df.columns.str.strip()

    st.dataframe(df)

    csv = df.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        label="Descargar pronósticos de cuartos",
        data=csv,
        file_name="pronosticos_cuartos.csv",
        mime="text/csv"
    )

else:
    st.info("Todavía no existen pronósticos registrados.")