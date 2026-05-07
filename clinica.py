import streamlit as st
import pandas as pd
import requests

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Diagnóstico Tarjeta Vida", layout="wide")

URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=1)
def cargar_y_analizar():
    try:
        # 1. Leemos la hoja de pacientes
        df = pd.read_csv(f"{URL_CSV}&sheet=pacientes", dtype=str).fillna("")
        
        # 2. LIMPIEZA AGRESIVA DE IDs
        # Buscamos en todas las columnas cuál parece ser la de identificación
        # Creamos una versión "limpia" de cada columna para buscar
        for col in df.columns:
            df[f"CLEAN_{col}"] = df[col].astype(str).str.split('.').str[0].str.replace(" ", "").strip()
        
        return df
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

st.title("🩺 Buscador Ultra-Robusto")

df_p = cargar_y_analizar()

if df_p is not None:
    # --- BUSCADOR ---
    busqueda = st.text_input("Ingresa el documento a buscar (sin puntos ni espacios)").strip()

    if busqueda:
        # Buscamos en TODAS las columnas limpias por si el ID se movió de lugar
        resultado = pd.DataFrame()
        columna_donde_se_hallo = ""
        
        for col in [c for c in df_p.columns if c.startswith("CLEAN_")]:
            match = df_p[df_p[col] == busqueda]
            if not match.empty:
                resultado = match
                columna_donde_se_hallo = col.replace("CLEAN_", "")
                break
        
        if not resultado.empty:
            p = resultado.iloc[0]
            st.success(f"¡PACIENTE ENCONTRADO! (Encontrado en la columna: {columna_donde_se_hallo})")
            
            # Mostrar datos en tarjetas
            st.markdown(f"""
            <div style="background-color: white; padding: 20px; border-radius: 10px; border-left: 10px solid #4fd1c5; color: black;">
                <h2>👤 {p.iloc[2]}</h2>
                <p><b>Documento:</b> {p.iloc[1]}</p>
                <p><b>EPS:</b> {p.iloc[5]} | <b>RH:</b> {p.iloc[6]}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error(f"No se encontró el ID '{busqueda}' en ninguna columna.")
            
            # --- SECCIÓN DE DIAGNÓSTICO (Solo aparece si falla) ---
            with st.expander("🛠️ Ver por qué falló (Análisis de datos real)"):
                st.write("Esta es la tabla que está llegando desde Google Sheets. Verifica que tu ID aparezca aquí:")
                # Mostramos solo las primeras columnas originales para diagnóstico
                columnas_reales = [c for c in df_p.columns if not c.startswith("CLEAN_")]
                st.dataframe(df_p[columnas_reales])
                
                st.write("IDs que el sistema ha procesado y está listo para reconocer:")
                # Mostramos los IDs que el sistema "entiende"
                if len(df_p.columns) > 1:
                    st.write(df_p.iloc[:, [1, -1]].head()) # Muestra col 2 y su versión limpia
else:
    st.warning("No se pudo cargar la base de datos. Revisa el link del Google Sheet.")
