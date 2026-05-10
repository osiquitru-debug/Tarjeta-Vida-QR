import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import qrcode
import io
import os
import tempfile

# ReportLab para el carnet
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from PIL import Image, ImageDraw, ImageFont

# --- 1. CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="Tarjeta Vida QR", layout="centered", page_icon="🩺")

LOGO_URL = "https://i.postimg.cc/bNJKtpsQ/vidaqr.jpg"
APP_BASE_URL = "https://tarjeta-vida-qr-abrilycompania.streamlit.app/"

if 'menu' not in st.session_state:
    st.session_state.menu = "Inicio"

# --- CAPTURA DE PARÁMETRO URL (para redirección desde QR) ---
query_params = st.query_params
if "doc" in query_params and st.session_state.menu != "Consulta":
    st.session_state.menu = "Consulta"
    st.session_state.doc_precargado = query_params["doc"]

bg_color = "#D8F3DC" if st.session_state.menu in ["Registrar", "Consulta"] else "#f0f7f4"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color} !important; color: #000000 !important; }}
    [data-testid="stSidebar"] {{ background-color: #E5B1B1 !important; border-right: 2px solid #d4a5a5; }}
    h1, h2, h3, p, span, label, li, div, .stMarkdown {{ color: #000000 !important; }}
    button[data-testid="stSidebarCollapseIcon"] svg,
    button[aria-label="Collapse sidebar"] svg,
    button[aria-label="Expand sidebar"] svg,
    .st-emotion-cache-6qob1r svg {{
        fill: #ffffff !important; color: #ffffff !important; stroke: #ffffff !important;
    }}
    button[data-testid="stSidebarCollapseIcon"],
    button[aria-label="Collapse sidebar"],
    button[aria-label="Expand sidebar"] {{ color: #ffffff !important; }}
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stTextArea>div>div>textarea {{
        background-color: #ffffff !important; color: #000000 !important; border: 1px solid #cbd5e1 !important;
    }}
    div.stButton > button {{
        background-color: #98FF98 !important; color: #000000 !important;
        border-radius: 10px !important; font-weight: bold !important; border: 1px solid #7ed37e !important;
    }}
    .medical-card {{
        background-color: #ffffff; padding: 20px; border-radius: 15px;
        border-left: 10px solid #a2d2ff; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px;
    }}
    .emergency-box {{
        background-color: #ffe5d9; padding: 12px; border-radius: 8px;
        border: 2px dashed #f43f5e; color: #b91c1c !important; font-weight: bold; margin-top: 10px;
    }}
    .evo-card {{
        background-color: #ffffff; padding: 15px; border-radius: 10px;
        border: 1px solid #e2e8f0; border-left: 8px solid #b7e4c7; margin-bottom: 12px;
    }}
    .grid-medidas {{
        display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin: 10px 0; padding: 5px 0;
        border-top: 1px solid #f1f5f9; border-bottom: 1px solid #f1f5f9;
    }}
    .footer {{
        position: fixed; left: 0; bottom: 0; width: 100%;
        text-align: center; color: #555555 !important; font-size: 0.8em; padding: 10px;
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
    except:
        return None, None

df_p, df_h = cargar_datos()

# --- 3. FUNCIÓN: GENERAR QR ---
def generar_qr_imagen(documento):
    """Genera QR y retorna un objeto PIL Image."""
    url_paciente = f"{APP_BASE_URL}?doc={documento}"
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=6, border=2)
    qr.add_data(url_paciente)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert("RGB")

def generar_qr_path(documento):
    """Genera QR y retorna path temporal."""
    img = generar_qr_imagen(documento)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    img.save(tmp.name)
    tmp.close()
    return tmp.name

# --- 4. FUNCIÓN: GENERAR CARNET PDF ---
def generar_carnet(paciente_data, alertas, nom_emer, tel_emer):
    """
    Genera un PDF estilo carnet VidaQR con cara frontal y posterior.
    Tamaño: CR80 (tarjeta de crédito) = 85.6mm x 54mm → en puntos: 242.7 x 153.0
    Para mejor impresión se usa escala x3: 728 x 459 pt (landscape)
    """
    # Dimensiones del carnet (puntos) ~ tarjeta crédito x3
    W = 728
    H = 459

    nombre    = paciente_data.get('NOMBRE', 'No registra')
    documento = paciente_data.get('DOCUMENTO', 'No registra')
    edad      = paciente_data.get('EDAD', 'No registra')
    eps       = paciente_data.get('EPS', 'No registra')
    rh        = paciente_data.get('RH', 'No registra')
    celular   = paciente_data.get('CELULAR', 'No registra')

    # Generar QR
    qr_path = generar_qr_path(documento.split('.')[0].replace(" ", "").strip())

    # Descargar logo
    logo_path = None
    try:
        r = requests.get(LOGO_URL, timeout=5)
        lt = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        lt.write(r.content)
        lt.close()
        logo_path = lt.name
    except:
        pass

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(W, H * 2 + 20))  # 2 caras apiladas con margen

    # =============================================
    # CARA FRONTAL (parte superior del PDF)
    # =============================================
    y_offset = H + 20  # cara frontal arriba

    # Fondo blanco con bordes redondeados simulados
    c.setFillColor(colors.white)
    c.roundRect(0, y_offset, W, H, 18, fill=1, stroke=0)

    # Franja azul marino inferior de la cara frontal
    c.setFillColor(colors.HexColor("#1a2e5a"))
    c.roundRect(0, y_offset, W, 72, 18, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#1a2e5a"))
    c.rect(0, y_offset + 18, W, 54, fill=1, stroke=0)

    # Íconos y texto de la franja inferior frontal
    iconos = [
        ("👨‍⚕️", "INFORMACIÓN\nMÉDICA", 60),
        ("💊", "MEDICAMENTOS", 210),
        ("🩺", "ALERGIAS", 340),
        ("📞", "CONTACTOS DE\nEMERGENCIA", 480),
    ]
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 7)
    for emoji, texto, x in iconos:
        c.setFont("Helvetica", 14)
        c.drawString(x, y_offset + 44, emoji)
        c.setFont("Helvetica-Bold", 6.5)
        for i, linea in enumerate(texto.split('\n')):
            c.drawString(x - 5, y_offset + 30 - i * 10, linea)

    # Texto eslogan
    c.setFillColor(colors.white)
    c.setFont("Helvetica-BoldOblique", 11)
    c.drawCentredString(W // 2 - 80, y_offset + 90, "Tu información de salud,")
    c.setFillColor(colors.HexColor("#98FF98"))
    c.setFont("Helvetica-BoldOblique", 12)
    c.drawCentredString(W // 2 - 80, y_offset + 76, "siempre contigo. ♥")

    # Logo (izquierda)
    if logo_path:
        try:
            c.drawImage(logo_path, 20, y_offset + H - 160, width=200, height=145, mask='auto')
        except:
            pass

    # Título "vida QR" grande — texto simulado
    c.setFillColor(colors.HexColor("#e91e8c"))
    c.setFont("Helvetica-Bold", 38)
    c.drawString(230, y_offset + H - 100, "vida")
    c.setFillColor(colors.HexColor("#1a2e5a"))
    c.setFont("Helvetica-Bold", 42)
    c.drawString(230, y_offset + H - 145, "QR")

    # Cruz médica decorativa
    c.setFillColor(colors.HexColor("#00bcd4"))
    c.setFont("Helvetica-Bold", 28)
    c.drawString(340, y_offset + H - 95, "✚")

    # Caja QR (derecha)
    qr_x = W - 175
    qr_y = y_offset + H - 195
    qr_size = 155
    # Marco teal del QR
    c.setFillColor(colors.HexColor("#00897b"))
    c.roundRect(qr_x - 8, qr_y - 38, qr_size + 16, qr_size + 46, 8, fill=1, stroke=0)
    # QR image
    try:
        c.drawImage(qr_path, qr_x, qr_y, width=qr_size, height=qr_size)
    except:
        pass
    # Etiqueta "ESCANEA EN EMERGENCIAS"
    c.setFillColor(colors.HexColor("#1a2e5a"))
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(colors.white)
    c.drawCentredString(qr_x + qr_size // 2, qr_y - 25, "ESCANEA EN EMERGENCIAS")

    # Caja rosada "EN CASO DE EMERGENCIA..."
    emer_x = W - 340
    emer_y = y_offset + 80
    c.setFillColor(colors.HexColor("#f06292"))
    c.roundRect(emer_x, emer_y, 155, 75, 8, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(emer_x + 22, emer_y + 55, "✚  EN CASO DE EMERGENCIA")
    c.drawString(emer_x + 18, emer_y + 40, "    ESTA TARJETA PUEDE")
    c.drawString(emer_x + 28, emer_y + 25, "      SALVAR TU VIDA")

    # Puntos decorativos de colores (simulados)
    decoraciones = [
        (colors.HexColor("#f9a825"), 390, y_offset + H - 20, 5),
        (colors.HexColor("#e91e8c"), 420, y_offset + H - 50, 4),
        (colors.HexColor("#7c4dff"), 200, y_offset + H - 30, 4),
        (colors.HexColor("#00bcd4"), 150, y_offset + 160, 5),
    ]
    for col, dx, dy, r in decoraciones:
        c.setFillColor(col)
        c.circle(dx, dy, r, fill=1, stroke=0)

    # =============================================
    # CARA POSTERIOR (parte inferior del PDF)
    # =============================================
    y_back = 0

    # Fondo blanco
    c.setFillColor(colors.white)
    c.roundRect(0, y_back, W, H, 18, fill=1, stroke=0)

    # Logo pequeño arriba izquierda
    if logo_path:
        try:
            c.drawImage(logo_path, 18, y_back + H - 120, width=130, height=95, mask='auto')
        except:
            pass

    # Subtítulo bajo logo
    c.setFillColor(colors.HexColor("#1a2e5a"))
    c.setFont("Helvetica-Bold", 7)
    c.drawString(22, y_back + H - 130, "TARJETA INTELIGENTE DE SALUD")

    # Estrella de vida (símbolo médico) - simulada con texto
    c.setFillColor(colors.HexColor("#00897b"))
    c.setFont("Helvetica-Bold", 40)
    c.drawString(55, y_back + 175, "✚")
    c.setFillColor(colors.HexColor("#1a2e5a"))
    c.setFont("Helvetica-Bold", 7)

    # USO RESPONSABLE
    c.setFillColor(colors.HexColor("#1a2e5a"))
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(20, y_back + 145, "🔒 USO RESPONSABLE")
    c.setFont("Helvetica", 6.5)
    c.setFillColor(colors.HexColor("#555555"))
    c.drawString(20, y_back + 133, "Esta tarjeta es personal")
    c.drawString(20, y_back + 122, "e intransferible.")

    # Tabla de información del titular
    tabla_x = 175
    tabla_y = y_back + H - 50
    tabla_w = W - tabla_x - 15
    row_h = 34

    # Encabezado tabla
    c.setFillColor(colors.HexColor("#00897b"))
    c.roundRect(tabla_x, tabla_y - 28, tabla_w, 30, 6, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(tabla_x + tabla_w // 2, tabla_y - 18, "INFORMACIÓN DEL TITULAR")

    # Filas de datos
    filas = [
        ("👤", "NOMBRE:", nombre),
        ("📅", "DOCUMENTO:", documento),
        ("🩸", "TIPO DE SANGRE:", rh),
        ("⚠️", "ALERGIAS / CONDICIONES:", alertas[:40] + ("..." if len(alertas) > 40 else "")),
        ("💊", "EPS:", eps),
        ("📞", "CONTACTO DE EMERGENCIA:", f"{nom_emer} - {tel_emer}"),
    ]

    for i, (icono, etiqueta, valor) in enumerate(filas):
        ry = tabla_y - 28 - (i + 1) * row_h
        # Fondo alterno
        if i % 2 == 0:
            c.setFillColor(colors.HexColor("#f8fffe"))
        else:
            c.setFillColor(colors.white)
        c.rect(tabla_x, ry, tabla_w, row_h, fill=1, stroke=0)
        # Línea divisoria
        c.setStrokeColor(colors.HexColor("#e0f2f1"))
        c.setLineWidth(0.5)
        c.line(tabla_x, ry, tabla_x + tabla_w, ry)

        # Ícono + etiqueta
        c.setFillColor(colors.HexColor("#00897b"))
        c.setFont("Helvetica", 9)
        c.drawString(tabla_x + 6, ry + 12, icono)
        c.setFillColor(colors.HexColor("#1a2e5a"))
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(tabla_x + 22, ry + 12, etiqueta)
        # Valor
        c.setFillColor(colors.HexColor("#333333"))
        c.setFont("Helvetica", 7.5)
        c.drawString(tabla_x + 22 + 148, ry + 12, str(valor))

    # Franja inferior 3 colores
    franja_y = y_back + 2
    franja_h = 42
    tercio = tabla_w // 3

    # Rosa
    c.setFillColor(colors.HexColor("#e91e8c"))
    c.roundRect(tabla_x, franja_y, tercio, franja_h, 8, fill=1, stroke=0)
    c.rect(tabla_x + 8, franja_y, tercio - 8, franja_h, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 6.5)
    c.drawString(tabla_x + 8, franja_y + 24, "🔒 TUS DATOS ESTÁN")
    c.drawString(tabla_x + 18, franja_y + 13, "PROTEGIDOS")

    # Verde azulado
    c.setFillColor(colors.HexColor("#00897b"))
    c.rect(tabla_x + tercio, franja_y, tercio, franja_h, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 6.5)
    c.drawString(tabla_x + tercio + 8, franja_y + 24, "⏰ ACCESO RÁPIDO")
    c.drawString(tabla_x + tercio + 14, franja_y + 13, "Y SEGURO")

    # Morado
    c.setFillColor(colors.HexColor("#7c4dff"))
    c.roundRect(tabla_x + 2 * tercio, franja_y, tercio, franja_h, 8, fill=1, stroke=0)
    c.rect(tabla_x + 2 * tercio, franja_y, tercio - 8, franja_h, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 6.5)
    c.drawString(tabla_x + 2 * tercio + 4, franja_y + 24, "⚙️ ACTUALIZA TU INFO")
    c.drawString(tabla_x + 2 * tercio + 8, franja_y + 13, "PERIÓDICAMENTE")

    # Puntos decorativos cara posterior
    deco2 = [
        (colors.HexColor("#f9a825"), W - 20, y_back + H - 40, 5),
        (colors.HexColor("#7c4dff"), W - 10, y_back + H - 80, 4),
        (colors.HexColor("#e91e8c"), 160, y_back + H - 20, 4),
    ]
    for col, dx, dy, r in deco2:
        c.setFillColor(col)
        c.circle(dx, dy, r, fill=1, stroke=0)

    c.save()

    # Limpiar temporales
    try:
        os.unlink(qr_path)
        if logo_path:
            os.unlink(logo_path)
    except:
        pass

    buf.seek(0)
    return buf.read()


# --- 5. NAVEGACIÓN ---
with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    if st.button("🏠 Inicio", use_container_width=True):
        st.session_state.menu = "Inicio"
        st.session_state.pop("doc_precargado", None)
        st.query_params.clear()
        st.rerun()
    if st.button("📝 Registrar", use_container_width=True):
        st.session_state.menu = "Registrar"
        st.session_state.pop("doc_precargado", None)
        st.query_params.clear()
        st.rerun()
    if st.button("🔍 Consulta", use_container_width=True):
        st.session_state.menu = "Consulta"
        st.session_state.pop("doc_precargado", None)
        st.query_params.clear()
        st.rerun()

# --- 6. VISTAS ---
st.image(LOGO_URL, width=220)

if st.session_state.menu == "Inicio":
    st.title("🩺 Tarjeta Vida QR")
    st.markdown("### *Tu Información de Salud Siempre Contigo*")
    st.markdown('<div class="footer">© 2026 Abril_Garcia_Sierra</div>', unsafe_allow_html=True)

elif st.session_state.menu == "Registrar":
    st.title("📝 REGISTRO DE PACIENTE")
    with st.form("f_reg", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nom = st.text_input("Nombre Completo")
            tdoc = st.selectbox("Tipo Doc", ["CC", "TI", "CE", "RC"])
            ndoc = st.text_input("Documento")
            cel = st.text_input("Celular")
        with c2:
            ed = st.text_input("Edad")
            ep = st.text_input("EPS")
            rh = st.selectbox("RH", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
        alert = st.text_area("Condiciones Especiales (Alergias, Enfermedades de base)")
        st.subheader("🚨 Emergencia")
        enom = st.text_input("Nombre Contacto")
        etel = st.text_input("Teléfono Contacto")
        if st.form_submit_button("GUARDAR PACIENTE"):
            payload = {
                "entry.346175428": nom, "entry.1650757004": tdoc, "entry.1302424820": ndoc,
                "entry.1801154005": ed, "entry.1172011247": ep, "entry.162368130": rh,
                "entry.1892763134": enom, "entry.2011749615": etel, "entry.celular_id": cel
            }
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse", data=payload)
            st.success("✅ Guardado.")
            st.cache_data.clear()

elif st.session_state.menu == "Consulta":
    st.title("🔍 CONSULTA CLÍNICA")

    doc_default = st.session_state.get("doc_precargado", "")
    id_buscado = st.text_input("Ingrese Documento", value=doc_default).strip().split('.')[0].replace(" ", "")

    if id_buscado and df_p is not None:
        paciente = df_p[df_p['ID_KEY'] == id_buscado]
        if not paciente.empty:
            p = paciente.iloc[0]

            def obtener_dato(df_row, palabras_clave):
                for col in df_row.index:
                    if all(palabra in col for palabra in palabras_clave):
                        return df_row[col]
                return "No registra"

            nom_emer = obtener_dato(p, ["NOMBRE", "CONTACTO", "EMERGENCIA"])
            tel_emer = obtener_dato(p, ["TEL", "CONTACTO", "EMERGENCIA"])
            alertas  = obtener_dato(p, ["CONDICIONES", "ESPECIALES"])

            st.markdown(f"""
            <div class="medical-card">
                <h2 style='margin:0;'>👤 {p.get('NOMBRE', 'No registra')}</h2>
                <p><b>ID:</b> {p.get('DOCUMENTO', 'No registra')} | <b>EDAD:</b> {p.get('EDAD', 'No registra')} | <b>RH:</b> {p.get('RH', 'No registra')}</p>
                <p><b>EPS:</b> {p.get('EPS', 'No registra')} | <b>CEL:</b> {p.get('CELULAR', 'No registra')}</p>
                <p><b>⚠️ ALERTAS:</b> {alertas}</p>
                <div class="emergency-box">🚨 EMERGENCIA: {nom_emer} (Tel: {tel_emer})</div>
            </div>""", unsafe_allow_html=True)

            h_p = df_h[df_h['ID_KEY'] == id_buscado].sort_index(ascending=False)

            # --- BOTONES DE DESCARGA ---
            col_pdf, col_carnet = st.columns(2)

            # PDF Historia Clínica
            with col_pdf:
                qr_path_pdf = generar_qr_path(id_buscado)
                pdf = FPDF()
                pdf.add_page()
                try:
                    logo_resp = requests.get(LOGO_URL, timeout=5)
                    logo_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
                    logo_tmp.write(logo_resp.content)
                    logo_tmp.close()
                    pdf.image(logo_tmp.name, 10, 8, 30)
                    os.unlink(logo_tmp.name)
                except:
                    pass
                try:
                    pdf.image(qr_path_pdf, x=165, y=8, w=35, h=35)
                    pdf.set_xy(155, 44)
                    pdf.set_font("Arial", 'I', 7)
                    pdf.cell(50, 4, "Escanea para ver historial", align='C')
                except:
                    pass
                pdf.set_xy(40, 10)
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(120, 10, "Historia Clinica - Tarjeta Vida QR", ln=False, align='C')
                pdf.ln(22)
                pdf.set_font("Arial", 'I', 8)
                pdf.set_text_color(80, 80, 80)
                pdf.cell(0, 5, f"Enlace directo: {APP_BASE_URL}?doc={id_buscado}", ln=True, align='C')
                pdf.set_text_color(0, 0, 0)
                pdf.ln(3)
                pdf.set_fill_color(230, 230, 230)
                pdf.set_font("Arial", 'B', 10)
                pdf.cell(0, 7, "DATOS DEL PACIENTE", 1, 1, 'L', 1)
                pdf.set_font("Arial", '', 9)
                info_p = (
                    f"Nombre: {p.get('NOMBRE')}\n"
                    f"Documento: {p.get('DOCUMENTO')} | Edad: {p.get('EDAD')} | RH: {p.get('RH')}\n"
                    f"EPS: {p.get('EPS')} | Celular: {p.get('CELULAR')}\n"
                    f"Alertas: {alertas}\n"
                    f"CONTACTO EMERGENCIA: {nom_emer} - Tel: {tel_emer}"
                )
                pdf.multi_cell(0, 5, info_p)
                pdf.ln(5)
                if not h_p.empty:
                    pdf.set_fill_color(183, 228, 199)
                    pdf.set_font("Arial", 'B', 10)
                    pdf.cell(0, 7, "HISTORIAL DE EVOLUCIONES", 1, 1, 'L', 1)
                    for _, f in h_p.iterrows():
                        pdf.set_fill_color(245, 245, 245)
                        pdf.set_font("Arial", 'B', 9)
                        pdf.cell(0, 6, f"FECHA: {f.get('MARCA TEMPORAL')}", 1, 1, 'L', 1)
                        pdf.set_font("Arial", '', 8)
                        txt_evo = (
                            f"MOTIVO: {f.get('3. MOTIVO DE LA CONSULTA')}\n"
                            f"VALORACION: {f.get('2. VALORACIÓN')}\n"
                            f"MEDIDAS: Talla: {f.get('4. TALLA')} | Peso: {f.get('5. PESO')} | TA: {f.get('6. PRESIÓN ARTERIAL')}\n"
                            f"ANTECEDENTES: {f.get('7. ANTECEDENTES MEDICOS')}\n"
                            f"TRATAMIENTO/MEDICAMENTOS: {f.get('8. MEDICAMENTOS')}\n"
                            f"LABORATORIOS: {f.get('9. LABORATORIOS - PROCEDIMIENTOS')}\n"
                            f"EPICRISIS: {f.get('10. EPICRISIS')}"
                        )
                        pdf.multi_cell(0, 4, txt_evo)
                        pdf.ln(2)
                try:
                    os.unlink(qr_path_pdf)
                except:
                    pass
                st.download_button(
                    "📥 Descargar Historia Clínica PDF",
                    pdf.output(dest='S').encode('latin-1'),
                    f"HC_{id_buscado}.pdf"
                )

            # Carnet VidaQR
            with col_carnet:
                carnet_bytes = generar_carnet(p, alertas, nom_emer, tel_emer)
                st.download_button(
                    "🪪 Descargar Carnet VidaQR",
                    carnet_bytes,
                    f"Carnet_VidaQR_{id_buscado}.pdf",
                    mime="application/pdf"
                )

            # --- QR EN PANTALLA ---
            st.markdown("---")
            st.subheader("📱 Código QR del Paciente")
            col1, col2 = st.columns([1, 2])
            with col1:
                url_paciente = f"{APP_BASE_URL}?doc={id_buscado}"
                qr2 = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=6, border=2)
                qr2.add_data(url_paciente)
                qr2.make(fit=True)
                img_qr2 = qr2.make_image(fill_color="black", back_color="white")
                buf_qr = io.BytesIO()
                img_qr2.save(buf_qr, format="PNG")
                buf_qr.seek(0)
                st.image(buf_qr, caption="Escanea para abrir la historia clínica", width=200)
            with col2:
                st.markdown(f"""
                **🔗 Enlace directo:**  
                `{url_paciente}`  

                Al escanear este QR se abrirá directamente  
                la historia clínica de **{p.get('NOMBRE', 'el paciente')}**.
                """)

            # --- FORMULARIO DE EVOLUCIÓN ---
            with st.expander("➕ REGISTRAR NUEVA EVOLUCIÓN"):
                with st.form("f_evo"):
                    c1, c2 = st.columns(2)
                    with c1:
                        v_mot = st.text_area("3. Motivo")
                        v_val = st.text_area("2. Valoración")
                        v_ant = st.text_area("7. Antecedentes")
                        v_tal = st.text_input("4. Talla")
                    with c2:
                        v_pes = st.text_input("5. Peso")
                        v_pre = st.text_input("6. Presión")
                        v_med = st.text_area("8. Medicamentos")
                        v_lab = st.text_area("9. Laboratorios")
                        v_epi = st.text_area("10. Epicrisis")
                    if st.form_submit_button("GUARDAR EVOLUCIÓN"):
                        data_e = {
                            "entry.2019369477": id_buscado, "entry.611862537": v_mot,
                            "entry.1088523869": v_val, "entry.1275746503": v_tal,
                            "entry.949747647": v_pes, "entry.2091389798": v_pre,
                            "entry.2016051626": v_med, "entry.616774918": v_epi
                        }
                        requests.post("https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse", data=data_e)
                        st.success("✅ Guardado.")
                        st.cache_data.clear()
                        st.rerun()

            # --- EVOLUCIONES ---
            st.subheader("📋 Evoluciones")
            if not h_p.empty:
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
                        <p><b>💊 MEDICAMENTOS:</b> {f.get('8. MEDICAMENTOS')}</p>
                        <p><b>🔬 LABS:</b> {f.get('9. LABORATORIOS - PROCEDIMIENTOS')}</p>
                        <p style='font-size:0.9em; color:#444; border-top:1px solid #eee; padding-top:5px;'>
                            <b>📝 EPICRISIS:</b> {f.get('10. EPICRISIS')}
                        </p>
                    </div>""", unsafe_allow_html=True)
        else:
            st.warning("⚠️ No se encontró ningún paciente con ese documento.")
