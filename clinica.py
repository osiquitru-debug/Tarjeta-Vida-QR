import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import segno
import io
import base64
import os

# --- 1. CONFIGURACIÓN VISUAL (MANTENIENDO TU ESTILO ORIGINAL AL 100%) ---
st.set_page_config(page_title="Tarjeta Vida QR", layout="centered", page_icon="🩺")

# URL del Logo Blindada (Usa la misma que te funcionaba)
LOGO_URL = "https://i.postimg.cc/bNJKtpsQ/vidaqr.jpg"

if 'menu' not in st.session_state: 
    st.session_state.menu = "Inicio"

bg_color = "#D8F3DC" if st.session_state.menu in ["Registrar", "Consulta"] else "#f0f7f4"

st.markdown(f"""
    <style>
    /* Fondo y texto general (Verde Medicinal) */
    .stApp {{ background-color: #D8F3DC !important; color: #000000 !important; }}
    [data-testid="stSidebar"] {{ background-color: #E5B1B1 !important; border-right: 2px solid #d4a5a5; }}
    
    /* CELDAS BLANCAS CON LETRA NEGRA (Forzado) */
    input, textarea, [data-baseweb="select"] > div {{
        background-color: #ffffff !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }}
    
    h1, h2, h3, p, span, label, li, div, .stMarkdown {{ color: #000000 !important; }}

    /* Botones Verde Menta Originales */
    div.stButton > button {{
        background-color: #98FF98 !important; 
        color: #000000 !important; 
        border-radius: 10px !important; 
        font-weight: bold !important; 
        border: 1px solid #7ed37e !important;
    }}
    
    /* Tarjeta Visual de Paciente */
    .medical-card {{
        background-color: #ffffff; padding: 20px; border-radius: 15px;
        border-left: 10px solid #a2d2ff; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px;
    }}
    
    /* Zona SOS en Pantalla */
    .emergency-box {{
        background-color: #ffe5d9; padding: 12px; border-radius: 8px;
        border: 2px dashed #f43f5e; color: #b91c1c !important; font-weight: bold; margin-top: 10px;
    }}
    
    /* Tarjeta Visual de Evoluciones */
    .evo-card {{
        background-color: #ffffff; padding: 15px; border-radius: 10px;
        border: 1px solid #e2e8f0; border-left: 8px solid #b7e4c7; margin-bottom: 12px;
    }}
    
    /* Grid de Medidas Visual */
    .grid-medidas {{ 
        display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin: 10px 0; padding: 5px 0;
        border-top: 1px solid #f1f5f9; border-bottom: 1px solid #f1f5f9;
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

# --- 3. BARRA LATERAL (TU NAVEGACIÓN ORIGINAL) ---
with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    if st.button("🏠 Inicio", use_container_width=True): st.session_state.menu = "Inicio"; st.rerun()
    if st.button("📝 Registrar", use_container_width=True): st.session_state.menu = "Registrar"; st.rerun()
    if st.button("🔍 Consulta", use_container_width=True): st.session_state.menu = "Consulta"; st.rerun()

# --- 4. VISTAS ---
st.image(LOGO_URL, width=220)

if st.session_state.menu == "Inicio":
    st.title("🩺 Tarjeta Vida QR")
    st.markdown("### *Tu Información de Salud Siempre Contigo*")
    # COPYRIGHT SOLICITADO
    st.markdown('<p style="text-align: center; color: #555;">© 2026 Vida QR - Abrilycompañia</p>', unsafe_allow_html=True)

elif st.session_state.menu == "Registrar":
    st.title("📝 REGISTRO DE PACIENTE")
    with st.form("f_reg", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nom = st.text_input("Nombre Completo"); tdoc = st.selectbox("Tipo Doc", ["CC", "TI", "CE", "RC"]); ndoc = st.text_input("Documento")
        with c2:
            ed = st.text_input("Edad"); ep = st.text_input("EPS"); rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        
        st.subheader("🚨 Contacto de Emergencia")
        enom = st.text_input("Nombre de Contacto"); etel = st.text_input("Teléfono de Contacto")
        if st.form_submit_button("GUARDAR PACIENTE"):
            payload = {"entry.346175428": nom, "entry.1650757004": tdoc, "entry.1302424820": ndoc, "entry.1801154005": ed, "entry.1172011247": ep, "entry.162368130": rh, "entry.1892763134": enom, "entry.2011749615": etel}
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
            st.success("✅ Paciente registrado."); st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.title("🔍 CONSULTA CLÍNICA")
    # Capturar el ID de la URL si existe (Para el escaneo del QR)
    id_buscado = st.text_input("Ingrese Documento", value=st.query_params.get("id", "")).strip()

    if id_buscado and df_p is not None:
        paciente = df_p[df_p['ID_KEY'] == id_buscado]
        if not paciente.empty:
            p = paciente.iloc[0]
            
            # --- GENERACIÓN DE QR FUNCIONAL (Punto 1) ---
            url_seguimiento = f"https://tarjeta-vida-qr-abrilycompania.streamlit.app/?id={id_buscado}"
            qr_gen = segno.make(url_seguimiento)
            qr_buf = io.BytesIO()
            qr_gen.save(qr_buf, kind='png', scale=10)
            qr_b64 = base64.b64encode(qr_buf.getvalue()).decode()

            # Mapeo de datos (Tu lógica original)
            def obtener_dato(df_row, palabras_clave):
                for col in df_row.index:
                    if all(palabra in col for palabra in palabras_clave):
                        return df_row[col]
                return "No registra"

            nom_emer = obtener_dato(p, ["NOMBRE", "CONTACTO", "EMERGENCIA"])
            tel_emer = obtener_dato(p, ["TEL", "CONTACTO", "EMERGENCIA"])

            st.markdown(f"""
            <div class="medical-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="flex:2;">
                        <h2 style='margin:0;'>👤 {p.get('NOMBRE')}</h2>
                        <p><b>ID:</b> {p.get('DOCUMENTO')} | <b>RH:</b> {p.get('RH')}</p>
                        <p><b>EPS:</b> {p.get('EPS')}</p>
                        <div class="emergency-box">🚨 EMERGENCIA: {nom_emer}<br>📞 Tel: {tel_emer}</div>
                    </div>
                    <div style="flex:1; text-align:center;">
                        <img src="data:image/png;base64,{qr_b64}" width="120">
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

            # --- BOTONES DE DESCARGA PDF ---
            col_pdf1, col_pdf2 = st.columns(2)
            
            with col_pdf1:
                # --- PDF CARNET ID-1 (85.6x53.98mm) (Punto 2 y 3: Respetando Imagen) ---
                # Configuración de página ID-1 en una hoja Carta para impresión centrado top
                pdf_c = FPDF(orientation='P', unit='mm', format='Letter')
                pdf_c.add_page()
                pdf_c.set_margins(0, 0, 0); pdf_c.set_auto_page_break(False)

                # Coordenadas ID-1 centrada top (Letter es 215.9 x 279.4)
                # Centrado: (215.9 - 85.6) / 2 = 65.15
                card_x = 65.15
                card_y = 20
                card_width = 85.6
                card_height = 53.98

                # 1. Base Caratula Azul Cielo
                pdf_c.set_fill_color(162, 210, 255); pdf_c.rect(card_x, card_y, card_width, card_height, 'F')
                
                # 2. Área QR Blanco
                qr_size = 28
                qr_x = card_x + 52 # A la derecha
                qr_y = card_y + 10 # Margen top
                pdf_c.set_fill_color(255, 255, 255); pdf_c.rect(qr_x, qr_y, qr_size, qr_size, 'F')
                
                # Insertar QR real
                tmp_qr_c = f"tmp_qr_c_{id_buscado}.png"; qr_gen.save(tmp_qr_c, border=0)
                pdf_c.image(tmp_qr_c, qr_x + 1, qr_y + 1, qr_size - 2)
                
                # 3. Logo y Textos
                try: pdf_c.image(LOGO_URL, card_x + 5, card_y + 5, 12)
                except: pass
                pdf_c.set_font("Arial", 'B', 11); pdf_c.set_xy(card_x + 20, card_y + 7); pdf_c.cell(30, 5, "TARJETA VIDA QR")
                
                pdf_c.set_font("Arial", 'B', 12); pdf_c.set_xy(card_x + 5, card_y + 18); pdf_c.cell(0, 6, p.get('NOMBRE')[:25])
                pdf_c.set_font("Arial", '', 8); pdf_c.set_xy(card_x + 5, card_y + 24); pdf_c.cell(0, 5, f"ID: {p.get('DOCUMENTO')}")
                pdf_c.set_xy(card_x + 5, card_y + 28); pdf_c.cell(0, 5, f"RH: {p.get('RH')} | EPS: {p.get('EPS')}")

                # 4. Zona SOS (Rectángulo Rojo abajo, full ancho)
                sos_height = 14
                pdf_c.set_fill_color(244, 63, 94); pdf_c.rect(card_x, card_y + card_height - sos_height, card_width, sos_height, 'F')
                pdf_c.set_text_color(255, 255, 255); pdf_c.set_font("Arial", 'B', 7)
                pdf_c.set_xy(card_x, card_y + card_height - sos_height + 1)
                pdf_c.cell(card_width, 5, f"🚨 CONTACTO EMERGENCIA: {nom_emer[:22]}", 0, 1, 'C')
                pdf_c.set_xy(card_x, card_y + card_height - sos_height + 5)
                pdf_c.cell(card_width, 5, f"📞 Tel: {tel_emer}", 0, 1, 'C')
                
                # Copyright PDF debajo de la tarjeta
                pdf_c.set_text_color(100, 100, 100); pdf_c.set_font("Arial", '', 6); pdf_c.set_xy(card_x, card_y + card_height + 1)
                pdf_c.cell(card_width, 4, "© 2026 Vida QR - Abrilycompañia", 0, 0, 'C')

                st.download_button("🪪 Descargar Carnet (Para Impresión 85x54mm)", pdf_c.output(dest='S').encode('latin-1'), f"Carnet_{id_buscado}.pdf")
                if os.path.exists(tmp_qr_c): os.remove(tmp_qr_c)

            with col_pdf2:
                # --- PDF HISTORIAL COMPLETO (Tu diseño original) ---
                pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", 'B', 14)
                pdf.cell(0, 10, "Historia Clinica Completa - Tarjeta Vida QR", ln=True, align='C')
                pdf.ln(5); pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", 'B', 10); pdf.cell(0, 7, "DATOS DEL PACIENTE", 1, 1, 'L', 1)
                pdf.set_font("Arial", '', 9)
                pdf.multi_cell(0, 5, f"Nombre: {p.get('NOMBRE')}\nDocumento: {p.get('DOCUMENTO')} | EPS: {p.get('EPS')}\nRH: {p.get('RH')}")
                st.download_button("📥 Descargar Reporte PDF Completo", pdf.output(dest='S').encode('latin-1'), f"HC_{id_buscado}.pdf")

            # --- EVOLUCIONES RECIENTES ---
            st.divider()
            h_p = df_h[df_h['ID_KEY'] == id_buscado].sort_index(ascending=False)
            if not h_p.empty:
                st.subheader("📋 Evoluciones Recientes")
                for _, f in h_p.iterrows():
                    st.markdown(f"""
                    <div class="evo-card">
                        <small>📅 {f.get('MARCA TEMPORAL')}</small>
                        <p><b>MOTIVO:</b> {f.get('3. MOTIVO DE LA CONSULTA')}</p>
                        <p><b>VALORACIÓN:</b> {f.get('2. VALORACIÓN')}</p>
                        <div class="grid-medidas">
                            <span><b>📏 Talla:</b> {f.get('4. TALLA')}</span>
                            <span><b>⚖️ Peso:</b> {f.get('5. PESO')}</span>
                            <span><b>🩸 TA:</b> {f.get('6. PRESIÓN ARTERIAL')}</span>
                        </div>
                        <p style='border-top:1px solid #eee; padding-top:5px;'><b>📝 EPICRISIS:</b> {f.get('10. EPICRISIS')}</p>
                    </div>""", unsafe_allow_html=True)
