import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import segno
import io
import base64
import os

# --- 1. CONFIGURACIÓN VISUAL (PÁGINA Y CARNET) ---
st.set_page_config(page_title="Tarjeta Vida QR", layout="centered", page_icon="🩺")

LOGO_URL = "https://i.postimg.cc/bNJKtpsQ/vidaqr.jpg"

if 'menu' not in st.session_state: 
    st.session_state.menu = "Inicio"

# Estética general de la plataforma
st.markdown(f"""
    <style>
    .stApp {{ background-color: #D8F3DC !important; color: #000000 !important; }}
    [data-testid="stSidebar"] {{ background-color: #E5B1B1 !important; }}
    h1, h2, h3, p, span, label, div {{ color: #000000 !important; font-family: 'Arial', sans-serif; }}
    
    /* DISEÑO DEL CARNET EN PANTALLA (IDÉNTICO A LA IMAGEN) */
    .carnet-container {{
        background-color: #a2d2ff; /* Azul cielo de la tarjeta */
        border-radius: 20px;
        padding: 25px;
        width: 100%;
        max-width: 480px;
        margin: 20px auto;
        border: 3px solid #ffffff;
        box-shadow: 0 12px 24px rgba(0,0,0,0.2);
    }}
    .carnet-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }}
    .carnet-body {{ display: flex; gap: 20px; }}
    .carnet-info {{ flex: 2; }}
    .carnet-qr-frame {{ 
        flex: 1; 
        background: white; 
        padding: 10px; 
        border-radius: 12px; 
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }}
    .label-sos-rojo {{
        background-color: #f43f5e; 
        color: white !important; 
        padding: 10px;
        border-radius: 8px; 
        font-size: 13px; 
        margin-top: 15px; 
        font-weight: bold; 
        text-align: center;
        border: 1px solid #ffffff;
    }}
    
    /* ESTILO DE TARJETAS DE EVOLUCIÓN (7 DE MAYO) */
    .evo-card {{
        background-color: #ffffff; padding: 18px; border-radius: 15px;
        border-left: 10px solid #b7e4c7; margin-bottom: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    }}
    .grid-datos {{ 
        display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; 
        background: #f8fafc; padding: 10px; border-radius: 8px; margin: 10px 0;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. CARGA DE DATOS ---
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=1)
def cargar_datos():
    try:
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes", dtype=str).fillna("No registra")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial", dtype=str).fillna("No registra")
        p.columns = [str(c).strip().upper() for c in p.columns]
        h.columns = [str(c).strip().upper() for c in h.columns]
        limpiar = lambda x: str(x).split('.')[0].replace(" ", "").strip()
        p['ID_KEY'] = p['DOCUMENTO'].apply(limpiar)
        h['ID_KEY'] = h['1. DOCUMENTO'].apply(limpiar)
        return p, h
    except: return None, None

df_p, df_h = cargar_datos()

# --- 3. NAVEGACIÓN ---
with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    if st.button("🏠 Inicio", use_container_width=True): st.session_state.menu = "Inicio"; st.rerun()
    if st.button("🔍 Consulta y Carnet", use_container_width=True): st.session_state.menu = "Consulta"; st.rerun()

# --- 4. VISTAS ---
if st.session_state.menu == "Inicio":
    st.title("🩺 Bienvenido a Vida QR")
    st.image(LOGO_URL, width=300)
    st.info("Sistema de gestión de carnetización y seguimiento de pacientes.")

elif st.session_state.menu == "Consulta":
    st.title("🔍 Consulta de Pacientes")
    id_buscado = st.text_input("Ingrese el Documento", value=st.query_params.get("id", "")).strip()

    if id_buscado and df_p is not None:
        paciente = df_p[df_p['ID_KEY'] == id_buscado]
        if not paciente.empty:
            p = paciente.iloc[0]
            
            # Datos de emergencia (dinámicos)
            nom_e = next((p[c] for c in p.index if "NOMBRE" in c and "EMERGENCIA" in c), "No registra")
            tel_e = next((p[c] for c in p.index if "TEL" in c and "EMERGENCIA" in c), "No registra")
            
            # Generar QR
            url_p = f"https://tarjeta-vida-qr-abrilycompania.streamlit.app/?id={id_buscado}"
            qr_segno = segno.make(url_p)
            buff_qr = io.BytesIO()
            qr_segno.save(buff_qr, kind='png', scale=10)
            qr_b64 = base64.b64encode(buff_qr.getvalue()).decode()

            # --- RENDER CARNET AZUL EN PANTALLA ---
            st.markdown(f"""
            <div class="carnet-container">
                <div class="carnet-header">
                    <img src="{LOGO_URL}" width="90">
                    <b style="font-size: 20px;">TARJETA VIDA QR</b>
                </div>
                <div class="carnet-body">
                    <div class="carnet-info">
                        <p style="font-size: 16px;"><b>PACIENTE:</b><br>{p.get('NOMBRE')}</p>
                        <p><b>DOCUMENTO:</b> {p.get('DOCUMENTO')}</p>
                        <p><b>RH:</b> {p.get('RH')} | <b>EPS:</b> {p.get('EPS')}</p>
                        <div class="label-sos-rojo">🚨 EMERGENCIA:<br>{nom_e} - {tel_e}</div>
                    </div>
                    <div class="carnet-qr-frame">
                        <img src="data:image/png;base64,{qr_b64}" width="110">
                        <b style="font-size: 10px; margin-top:5px; color:#333;">ESCANÉAME</b>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

            # --- GENERACIÓN DE PDF PROFESIONAL ---
            pdf = FPDF(orientation='L', unit='mm', format=(85, 55))
            pdf.add_page()
            
            # Fondo Azul Cielo
            pdf.set_fill_color(162, 210, 255)
            pdf.rect(0, 0, 85, 55, 'F')
            
            # Manejo de imágenes temporales para evitar errores de servidor
            logo_path = "logo_temp.jpg"
            qr_path = f"qr_{id_buscado}.png"
            
            try:
                # Descargar Logo si no existe
                if not os.path.exists(logo_path):
                    r_logo = requests.get(LOGO_URL)
                    with open(logo_path, "wb") as fl: fl.write(r_logo.content)
                pdf.image(logo_path, 5, 5, 18)
                
                # Guardar QR Físico
                qr_segno.save(qr_path, border=0)
                
                # Dibujar recuadro blanco para el QR (Estética imagen)
                pdf.set_fill_color(255, 255, 255)
                pdf.rect(54, 12, 26, 32, 'F')
                pdf.image(qr_path, 56, 14, 22, 22)
                
                pdf.set_font("Arial", 'B', 6)
                pdf.set_text_color(0, 0, 0)
                pdf.set_xy(54, 38); pdf.cell(26, 4, f"ID: {id_buscado}", 0, 0, 'C')
            except: pass

            # Texto del PDF
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", 'B', 10); pdf.set_xy(25, 7); pdf.cell(0, 5, "TARJETA VIDA QR")
            
            pdf.set_font("Arial", 'B', 8); pdf.set_xy(5, 18); pdf.cell(0, 4, "PACIENTE:")
            pdf.set_font("Arial", '', 8); pdf.set_xy(5, 22); pdf.cell(0, 4, f"{p.get('NOMBRE')[:30]}")
            pdf.set_xy(5, 27); pdf.cell(0, 4, f"ID: {p.get('DOCUMENTO')}")
            pdf.set_xy(5, 31); pdf.cell(0, 4, f"RH: {p.get('RH')} | EPS: {p.get('EPS')}")
            
            # Recuadro SOS Rojo en PDF
            pdf.set_fill_color(244, 63, 94)
            pdf.rect(5, 38, 45, 12, 'F')
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Arial", 'B', 7)
            pdf.set_xy(5, 39); pdf.multi_cell(45, 3.5, f"SOS: {nom_e[:20]}\nTEL: {tel_e}", 0, 'C')

            st.download_button("📥 Descargar Carnet Digital (PDF)", pdf.output(dest='S').encode('latin-1'), f"Carnet_{id_buscado}.pdf")
            
            # Borrar QR temporal
            if os.path.exists(qr_path): os.remove(qr_path)

            # --- HISTORIAL CLÍNICO (ESTÉTICA 7 DE MAYO) ---
            st.divider()
            st.subheader("📋 Historia Clínica y Evoluciones")
            
            h_p = df_h[df_h['ID_KEY'] == id_buscado].sort_index(ascending=False)
            
            if not h_p.empty:
                for _, f in h_p.iterrows():
                    st.markdown(f"""
                    <div class="evo-card">
                        <div style="display: flex; justify-content: space-between;">
                            <small>📅 <b>FECHA:</b> {f.get('MARCA TEMPORAL')}</small>
                            <span style="color: #2d6a4f; font-weight: bold;">Evolución Médica</span>
                        </div>
                        <p style="margin-top:10px;"><b>MOTIVO DE CONSULTA:</b><br>{f.get('3. MOTIVO DE LA CONSULTA')}</p>
                        <div class="grid-datos">
                            <span><b>📏 Talla:</b> {f.get('4. TALLA')} cm</span>
                            <span><b>⚖️ Peso:</b> {f.get('5. PESO')} kg</span>
                            <span><b>🩸 TA:</b> {f.get('6. PRESIÓN ARTERIAL')}</span>
                        </div>
                        <p><b>📝 VALORACIÓN Y EPICRISIS:</b><br>{f.get('10. EPICRISIS')}</p>
                    </div>""", unsafe_allow_html=True)
            else:
                st.warning("No hay evoluciones registradas para este paciente.")
