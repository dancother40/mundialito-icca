import streamlit as st
import pandas as pd
import os


ARCHIVO_PARTIDOS = "partidos_octavos.csv"
ARCHIVO_CANDIDATOS = "posibles_ganadores.csv"
ARCHIVO_PRONOSTICOS = "pronosticos_octavos.csv"
ARCHIVO_GANADORES = "ganadores_octavos.csv"


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


st.title("Mundialito - Octavos de Final")
st.write("Ingreso de pronósticos de octavos y posible ganador del torneo")

st.divider()

if not os.path.exists(ARCHIVO_PARTIDOS):
    st.error("No existe el archivo partidos_octavos.csv.")
    st.stop()

if not os.path.exists(ARCHIVO_CANDIDATOS):
    st.error("No existe el archivo posibles_ganadores.csv.")
    st.stop()


df_partidos = leer_csv_seguro(ARCHIVO_PARTIDOS)
df_candidatos = leer_csv_seguro(ARCHIVO_CANDIDATOS)

df_partidos.columns = df_partidos.columns.str.strip()
df_candidatos.columns = df_candidatos.columns.str.strip()


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
    st.error(f"Faltan columnas en partidos_octavos.csv: {faltantes_partidos}")
    st.stop()


if "candidato" not in df_candidatos.columns:
    st.error("Falta la columna 'candidato' en posibles_ganadores.csv.")
    st.stop()


df_partidos["id_partido"] = df_partidos["id_partido"].astype(int)

candidatos = (
    df_candidatos["candidato"]
    .dropna()
    .astype(str)
    .str.strip()
    .tolist()
)

if len(candidatos) == 0:
    st.error("No existen candidatos en posibles_ganadores.csv.")
    st.stop()


nombre = st.text_input("Nombre del participante")

ganador_torneo = st.selectbox(
    "Selecciona tu posible ganador del Mundial",
    options=["Selecciona una opción"] + candidatos
)

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

if st.button("Guardar pronósticos de octavos"):

    if nombre.strip() == "":
        st.error("Debes escribir tu nombre.")

    elif ganador_torneo == "Selecciona una opción":
        st.error("Debes seleccionar un posible ganador del Mundial.")

    else:
        registros_pronosticos = []

        for p in pronosticos:
            registros_pronosticos.append({
                "nombre": nombre.strip(),
                "id_partido": p["id_partido"],
                "fase": p["fase"],
                "equipo_a": p["equipo_a"],
                "equipo_b": p["equipo_b"],
                "goles_a": p["goles_a"],
                "goles_b": p["goles_b"]
            })

        nuevo_df_pronosticos = pd.DataFrame(registros_pronosticos)

        if os.path.exists(ARCHIVO_PRONOSTICOS):
            df_existente_pronosticos = leer_csv_seguro(ARCHIVO_PRONOSTICOS)
            df_existente_pronosticos.columns = df_existente_pronosticos.columns.str.strip()

            df_final_pronosticos = pd.concat(
                [df_existente_pronosticos, nuevo_df_pronosticos],
                ignore_index=True
            )

        else:
            df_final_pronosticos = nuevo_df_pronosticos

        df_final_pronosticos.to_csv(
            ARCHIVO_PRONOSTICOS,
            index=False,
            encoding="utf-8-sig"
        )

        nuevo_df_ganador = pd.DataFrame([{
            "nombre": nombre.strip(),
            "ganador_torneo": ganador_torneo
        }])

        if os.path.exists(ARCHIVO_GANADORES):
            df_existente_ganadores = leer_csv_seguro(ARCHIVO_GANADORES)
            df_existente_ganadores.columns = df_existente_ganadores.columns.str.strip()

            df_final_ganadores = pd.concat(
                [df_existente_ganadores, nuevo_df_ganador],
                ignore_index=True
            )

        else:
            df_final_ganadores = nuevo_df_ganador

        df_final_ganadores.to_csv(
            ARCHIVO_GANADORES,
            index=False,
            encoding="utf-8-sig"
        )

        st.success("Pronósticos y posible ganador guardados correctamente.")


st.divider()

st.subheader("Pronósticos registrados")

if os.path.exists(ARCHIVO_PRONOSTICOS):

    df_pronosticos = leer_csv_seguro(ARCHIVO_PRONOSTICOS)
    df_pronosticos.columns = df_pronosticos.columns.str.strip()

    st.dataframe(df_pronosticos)

    csv_pronosticos = df_pronosticos.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        label="Descargar pronósticos de octavos",
        data=csv_pronosticos,
        file_name="pronosticos_octavos.csv",
        mime="text/csv"
    )

else:
    st.info("Todavía no existen pronósticos registrados.")


st.divider()

st.subheader("Posibles ganadores registrados")

if os.path.exists(ARCHIVO_GANADORES):

    df_ganadores = leer_csv_seguro(ARCHIVO_GANADORES)
    df_ganadores.columns = df_ganadores.columns.str.strip()

    st.dataframe(df_ganadores)

    csv_ganadores = df_ganadores.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        label="Descargar posibles ganadores",
        data=csv_ganadores,
        file_name="ganadores_octavos.csv",
        mime="text/csv"
    )

else:
    st.info("Todavía no existen posibles ganadores registrados.")