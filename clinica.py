import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import qrcode
import io
import os
import tempfile
import hashlib

from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm

# ─────────────────────────────────────────────
# 1. CONFIGURACIÓN VISUAL
# ─────────────────────────────────────────────
st.set_page_config(page_title="Tarjeta Vida QR", layout="centered", page_icon="🩺")

LOGO_URL     = "https://i.postimg.cc/bNJKtpsQ/vidaqr.jpg"
APP_BASE_URL = "https://tarjeta-vida-qr-abrilycompania.streamlit.app/"

# ─────────────────────────────────────────────
# 2. USUARIOS AUTORIZADOS
# ─────────────────────────────────────────────
def _hash(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()

USUARIOS = {
    "admin": _hash("VidaQR2026"),
    "abril": _hash("abril123"),
}

# ─────────────────────────────────────────────
# 3. ESTADO DE SESIÓN INICIAL
# ─────────────────────────────────────────────
for key, val in {
    "menu": "Inicio",
    "autenticado": False,
    "usuario_activo": "",
    "acceso_qr": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# Detectar apertura por QR (?doc=...)
query_params = st.query_params
if "doc" in query_params and st.session_state.menu != "Consulta":
    st.session_state.menu = "Consulta"
    st.session_state.doc_precargado = query_params["doc"]
    st.session_state.acceso_qr = True

bg_color = "#D8F3DC" if st.session_state.menu in ["Registrar", "Consulta"] else "#f0f7f4"

st.markdown(f"""
<style>
.stApp{{background-color:{bg_color}!important;color:#000!important;}}
[data-testid="stSidebar"]{{background-color:#E5B1B1!important;border-right:2px solid #d4a5a5;}}
h1,h2,h3,p,span,label,li,div,.stMarkdown{{color:#000!important;}}
button[data-testid="stSidebarCollapseIcon"] svg,
button[aria-label="Collapse sidebar"] svg,
button[aria-label="Expand sidebar"] svg{{fill:#fff!important;color:#fff!important;stroke:#fff!important;}}
.stTextInput>div>div>input,.stSelectbox>div>div>div,.stTextArea>div>div>textarea{{
  background-color:#fff!important;color:#000!important;border:1px solid #cbd5e1!important;}}
div.stButton>button{{background-color:#98FF98!important;color:#000!important;
  border-radius:10px!important;font-weight:bold!important;border:1px solid #7ed37e!important;}}
.medical-card{{background:#fff;padding:20px;border-radius:15px;
  border-left:10px solid #a2d2ff;box-shadow:0 4px 6px rgba(0,0,0,.05);margin-bottom:20px;}}
.emergency-box{{background:#ffe5d9;padding:12px;border-radius:8px;
  border:2px dashed #f43f5e;color:#b91c1c!important;font-weight:bold;margin-top:10px;}}
.evo-card{{background:#fff;padding:15px;border-radius:10px;
  border:1px solid #e2e8f0;border-left:8px solid #b7e4c7;margin-bottom:12px;}}
.grid-medidas{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;
  margin:10px 0;padding:5px 0;border-top:1px solid #f1f5f9;border-bottom:1px solid #f1f5f9;}}
.login-box{{background:#fff;padding:28px 24px;border-radius:16px;
  border:2px solid #a2d2ff;box-shadow:0 6px 20px rgba(0,0,0,.08);margin-top:20px;}}
.badge-qr{{background:#d8f3dc;border:1px solid #74c69d;border-radius:8px;
  padding:8px 14px;font-size:.85em;margin-bottom:12px;display:inline-block;}}
.footer{{position:fixed;left:0;bottom:0;width:100%;
  text-align:center;color:#555!important;font-size:.8em;padding:10px;}}
</style>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 4. CARGA DE DATOS
# ─────────────────────────────────────────────
URL_CSV = "https://docs.google.com/spreadsheets/d/18Ohfwj5TkaoRf3oPFpPxpPYhHTpccfLpG5r30MXEvC0/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=1)
def cargar_datos():
    try:
        p = pd.read_csv(f"{URL_CSV}&sheet=pacientes", dtype=str).fillna("No registra")
        h = pd.read_csv(f"{URL_CSV}&sheet=historial", dtype=str).fillna("No registra")
        p.columns = [str(c).strip().upper() for c in p.columns]
        h.columns = [str(c).strip().upper() for c in h.columns]
        limpiar = lambda x: str(x).split(".")[0].replace(" ", "").strip()
        p["ID_KEY"] = p["DOCUMENTO"].apply(limpiar)
        h["ID_KEY"] = h["1. DOCUMENTO"].apply(limpiar)
        return p, h
    except:
        return None, None

df_p, df_h = cargar_datos()

# ─────────────────────────────────────────────
# 5. UTILIDADES QR
# ─────────────────────────────────────────────
def _qr_image(documento):
    url = f"{APP_BASE_URL}?doc={documento}"
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H,
                       box_size=8, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert("RGB")

def qr_path(documento):
    img = _qr_image(documento)
    t = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    img.save(t.name); t.close()
    return t.name

def qr_bytes(documento):
    img = _qr_image(documento)
    buf = io.BytesIO(); img.save(buf, format="PNG"); buf.seek(0)
    return buf

def logo_path_tmp():
    try:
        r = requests.get(LOGO_URL, timeout=6)
        t = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        t.write(r.content); t.close()
        return t.name
    except:
        return None

# ─────────────────────────────────────────────
# 6. GENERADOR DE CARNET CR80 (85.6 × 54 mm)
# ─────────────────────────────────────────────
def generar_carnet(p, alertas, nom_emer, tel_emer):
    W = 85.6 * mm
    H = 54.0 * mm

    doc_raw = str(p.get("DOCUMENTO", "")).split(".")[0].replace(" ", "").strip()
    nombre  = str(p.get("NOMBRE",    "No registra"))
    rh      = str(p.get("RH",        "No registra"))
    eps     = str(p.get("EPS",       "No registra"))

    _qr  = qr_path(doc_raw)
    _log = logo_path_tmp()

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(W, H))

    # ── PÁGINA 1: CARA FRONTAL ────────────────
    c.setFillColor(colors.white)
    c.roundRect(0, 0, W, H, 4*mm, fill=1, stroke=0)

    franja_h = 15 * mm
    c.setFillColor(colors.HexColor("#1B2E5E"))
    c.roundRect(0, 0, W, franja_h, 4*mm, fill=1, stroke=0)
    c.rect(0, 4*mm, W, franja_h - 4*mm, fill=1, stroke=0)

    p_wave = c.beginPath()
    p_wave.moveTo(0, franja_h)
    p_wave.curveTo(W*0.25, franja_h+4*mm, W*0.55, franja_h-3*mm, W*0.78, franja_h+2*mm)
    p_wave.curveTo(W*0.88, franja_h+4*mm, W*0.95, franja_h+1*mm, W, franja_h)
    p_wave.lineTo(W, 0); p_wave.lineTo(0, 0); p_wave.close()
    c.drawPath(p_wave, fill=1, stroke=0)

    for icon, texto, ix in [
        ("🩺", "INFORMACIÓN\nMÉDICA",      W*0.08),
        ("💊", "MEDICAMENTOS",              W*0.30),
        ("⚠️", "ALERGIAS",                 W*0.52),
        ("📞", "CONTACTOS DE\nEMERGENCIA", W*0.72),
    ]:
        c.setFillColor(colors.white)
        c.setFont("Helvetica", 5.5)
        c.drawCentredString(ix, 9.5*mm, icon)
        c.setFont("Helvetica-Bold", 3.5)
        for j, linea in enumerate(texto.split("\n")):
            c.drawCentredString(ix, 6.5*mm - j*3.2, linea)

    c.setFillColor(colors.HexColor("#1B2E5E"))
    c.setFont("Helvetica-Oblique", 5.2)
    c.drawString(2*mm, franja_h+1.5*mm, "Tu información de salud,")
    c.setFillColor(colors.HexColor("#00897b"))
    c.setFont("Helvetica-BoldOblique", 5.5)
    c.drawString(2*mm, franja_h-1.5*mm, "siempre contigo. ♥")

    if _log:
        try:
            c.drawImage(_log, 1.5*mm, franja_h+3*mm, width=28*mm, height=20*mm,
                        preserveAspectRatio=True, mask="auto")
        except: pass

    c.setFillColor(colors.HexColor("#00bcd4"))
    c.setFont("Helvetica-Bold", 9)
    c.drawString(30*mm, H-10*mm, "✚")

    for col, dx, dy, r in [
        (colors.HexColor("#f9a825"), W-5*mm, H-4*mm,  1.2*mm),
        (colors.HexColor("#e91e8c"), W-8*mm, H-8*mm,  0.9*mm),
        (colors.HexColor("#7c4dff"), W-3*mm, H-12*mm, 0.9*mm),
        (colors.HexColor("#00bcd4"), 2*mm,   H-4*mm,  0.8*mm),
        (colors.HexColor("#f9a825"), 5*mm,   H-7*mm,  0.7*mm),
        (colors.HexColor("#e91e8c"), W-4*mm, H-20*mm, 0.7*mm),
    ]:
        c.setFillColor(col); c.circle(dx, dy, r, fill=1, stroke=0)

    c.setFillColor(colors.HexColor("#7c4dff"))
    c.setFont("Helvetica-Bold", 7)
    c.drawString(W-10*mm, H-6*mm, "+")
    c.setFillColor(colors.HexColor("#00bcd4"))
    c.drawString(W-14*mm, H-14*mm, "+")

    qr_size = 20*mm
    qr_x = W - qr_size - 2*mm
    qr_y = H - qr_size - 2.5*mm
    c.setFillColor(colors.HexColor("#00897b"))
    c.roundRect(qr_x-1.5*mm, qr_y-5*mm, qr_size+3*mm, qr_size+6.5*mm, 2*mm, fill=1, stroke=0)
    try: c.drawImage(_qr, qr_x, qr_y, width=qr_size, height=qr_size)
    except: pass
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 3.2)
    c.drawCentredString(qr_x+qr_size/2, qr_y-3.5*mm, "ESCANEA EN EMERGENCIAS")

    ebox_x = W - qr_size - 2*mm - 30*mm - 1*mm
    ebox_y = franja_h + 2.5*mm
    ebox_w = 29*mm; ebox_h = 12*mm
    c.setFillColor(colors.HexColor("#f06292"))
    c.roundRect(ebox_x, ebox_y, ebox_w, ebox_h, 2*mm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 3.8)
    c.drawCentredString(ebox_x+ebox_w/2, ebox_y+7.5*mm, "✚  EN CASO DE EMERGENCIA")
    c.setFont("Helvetica-Bold", 3.5)
    c.drawCentredString(ebox_x+ebox_w/2, ebox_y+4.5*mm, "ESTA TARJETA PUEDE")
    c.drawCentredString(ebox_x+ebox_w/2, ebox_y+1.8*mm, "SALVAR TU VIDA")
    c.showPage()

    # ── PÁGINA 2: CARA POSTERIOR ──────────────
    c.setFillColor(colors.white)
    c.roundRect(0, 0, W, H, 4*mm, fill=1, stroke=0)

    bot_h = 8*mm; tercio = W/3
    c.setFillColor(colors.HexColor("#e91e8c"))
    c.roundRect(0, 0, tercio, bot_h, 4*mm, fill=1, stroke=0)
    c.rect(4*mm, 0, tercio-4*mm, bot_h, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#00897b"))
    c.rect(tercio, 0, tercio, bot_h, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#7c4dff"))
    c.roundRect(2*tercio, 0, tercio, bot_h, 4*mm, fill=1, stroke=0)
    c.rect(2*tercio, 0, tercio-4*mm, bot_h, fill=1, stroke=0)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 3.0)
    c.drawCentredString(tercio/2,          5.2*mm, "🔒 TUS DATOS ESTÁN")
    c.drawCentredString(tercio/2,          2.5*mm, "PROTEGIDOS")
    c.drawCentredString(tercio+tercio/2,   5.2*mm, "⏰ ACCESO RÁPIDO")
    c.drawCentredString(tercio+tercio/2,   2.5*mm, "Y SEGURO 24/7")
    c.drawCentredString(2*tercio+tercio/2, 5.2*mm, "⚙️ ACTUALIZA TU INFO")
    c.drawCentredString(2*tercio+tercio/2, 2.5*mm, "PERIÓDICAMENTE")

    if _log:
        try:
            c.drawImage(_log, 1.5*mm, H-18*mm, width=22*mm, height=15*mm,
                        preserveAspectRatio=True, mask="auto")
        except: pass

    c.setFillColor(colors.HexColor("#1B2E5E"))
    c.setFont("Helvetica-Bold", 3.0)
    c.drawString(1.8*mm, H-20*mm, "TARJETA INTELIGENTE DE SALUD")
    c.setFillColor(colors.HexColor("#00897b"))
    c.setFont("Helvetica-Bold", 16)
    c.drawString(5*mm, H-38*mm, "✚")
    c.setFillColor(colors.HexColor("#1B2E5E"))
    c.setFont("Helvetica-Bold", 3.2)
    c.drawString(1.8*mm, H-41*mm, "🔒 USO RESPONSABLE")
    c.setFillColor(colors.HexColor("#555555"))
    c.setFont("Helvetica", 2.8)
    c.drawString(1.8*mm, H-44*mm, "Esta tarjeta es personal")
    c.drawString(1.8*mm, H-46.5*mm, "e intransferible.")

    for col, dx, dy, r in [
        (colors.HexColor("#f9a825"), W-4*mm, H-4*mm,  1.0*mm),
        (colors.HexColor("#7c4dff"), W-3*mm, H-10*mm, 0.8*mm),
        (colors.HexColor("#e91e8c"), W-7*mm, H-4*mm,  0.7*mm),
        (colors.HexColor("#00bcd4"), W-6*mm, H-15*mm, 0.7*mm),
    ]:
        c.setFillColor(col); c.circle(dx, dy, r, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#7c4dff"))
    c.setFont("Helvetica-Bold", 6)
    c.drawString(W-9*mm, H-6*mm, "+")

    tab_x = 26*mm; tab_y = H-2*mm; tab_w = W-tab_x-1.5*mm; head_h = 6*mm
    c.setFillColor(colors.HexColor("#00897b"))
    c.roundRect(tab_x, tab_y-head_h, tab_w, head_h, 2*mm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 4.5)
    c.drawCentredString(tab_x+tab_w/2, tab_y-head_h+2*mm, "INFORMACIÓN DEL TITULAR")

    for i, (icon, label, valor) in enumerate([
        ("👤", "NOMBRE:",              nombre[:28]),
        ("🪪", "DOCUMENTO:",           doc_raw),
        ("🩸", "TIPO DE SANGRE:",      rh),
        ("⚠️", "ALERGIAS:",            (alertas[:28]+"…") if len(alertas)>28 else alertas),
        ("💊", "EPS:",                 eps[:24]),
        ("📞", "CONTACTO EMERGENCIA:", f"{nom_emer[:16]} {tel_emer[:12]}"),
    ]):
        ry = tab_y - head_h - (i+1)*7.2*mm
        c.setFillColor(colors.HexColor("#f0fdfa") if i%2==0 else colors.white)
        c.rect(tab_x, ry, tab_w, 7.2*mm, fill=1, stroke=0)
        c.setStrokeColor(colors.HexColor("#b2dfdb")); c.setLineWidth(0.3)
        c.line(tab_x, ry+7.2*mm, tab_x+tab_w, ry+7.2*mm)
        c.setFont("Helvetica", 4.2); c.setFillColor(colors.HexColor("#00897b"))
        c.drawString(tab_x+1*mm, ry+2.5*mm, icon)
        c.setFont("Helvetica-Bold", 3.5); c.setFillColor(colors.HexColor("#1B2E5E"))
        c.drawString(tab_x+4.5*mm, ry+4.2*mm, label)
        c.setFont("Helvetica", 3.5); c.setFillColor(colors.HexColor("#333333"))
        c.drawString(tab_x+4.5*mm, ry+1.5*mm, str(valor))

    c.showPage(); c.save()
    for f in [_qr, _log]:
        try:
            if f: os.unlink(f)
        except: pass
    buf.seek(0)
    return buf.read()


# ─────────────────────────────────────────────
# 7. NAVEGACIÓN (SIDEBAR)
# ─────────────────────────────────────────────
with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)

    if st.session_state.autenticado:
        st.success(f"✅ {st.session_state.usuario_activo}")
        if st.button("🚪 Cerrar sesión", use_container_width=True):
            st.session_state.autenticado    = False
            st.session_state.usuario_activo = ""
            st.session_state.menu           = "Inicio"
            st.session_state.acceso_qr      = False
            st.query_params.clear(); st.rerun()
    else:
        st.info("🔒 No has iniciado sesión")

    st.markdown("---")

    if st.button("🏠 Inicio", use_container_width=True):
        st.session_state.menu      = "Inicio"
        st.session_state.acceso_qr = False
        st.session_state.pop("doc_precargado", None)
        st.query_params.clear(); st.rerun()

    if st.button("📝 Registrar", use_container_width=True):
        st.session_state.menu      = "Registrar"
        st.session_state.acceso_qr = False
        st.session_state.pop("doc_precargado", None)
        st.query_params.clear(); st.rerun()

    if st.button("🔍 Consulta", use_container_width=True):
        st.session_state.menu      = "Consulta"
        st.session_state.acceso_qr = False
        st.session_state.pop("doc_precargado", None)
        st.query_params.clear(); st.rerun()


# ─────────────────────────────────────────────
# 8. VISTAS
# ─────────────────────────────────────────────
st.image(LOGO_URL, width=220)

# ══════════════════════════════════════════════
# INICIO — bienvenida + login integrado
# ══════════════════════════════════════════════
if st.session_state.menu == "Inicio":
    st.title("🩺 Tarjeta Vida QR")
    st.markdown("### *Tu Información de Salud Siempre Contigo*")

    st.markdown("""
    <div style='background:#fff;padding:18px;border-radius:12px;border:1px solid #a2d2ff;margin-bottom:20px;'>
        <b>📌 ¿Cómo funciona?</b><br><br>
        🔍 <b>Escanear QR</b> → Abre historial e historial del paciente sin login.<br><br>
        📝 <b>Registrar paciente</b> → Requiere usuario y contraseña.<br><br>
        🩺 <b>Consulta + Evoluciones</b> → Disponible para todos.
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.autenticado:
        st.success(f"✅ Sesión activa como **{st.session_state.usuario_activo}**. "
                   "Ahora puedes acceder a **Registrar** desde el menú.")
    else:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown("#### 🔐 Iniciar sesión — Personal autorizado")
        st.markdown("Inicia sesión para habilitar el registro de pacientes.")

        with st.form("form_login_inicio"):
            usuario = st.text_input("👤 Usuario")
            clave   = st.text_input("🔑 Contraseña", type="password")
            entrar  = st.form_submit_button("INGRESAR", use_container_width=True)

            if entrar:
                if usuario in USUARIOS and USUARIOS[usuario] == _hash(clave):
                    st.session_state.autenticado    = True
                    st.session_state.usuario_activo = usuario
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos.")

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="footer">© 2026 Abril_Garcia_Sierra</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# REGISTRAR — protegido por login
# ══════════════════════════════════════════════
elif st.session_state.menu == "Registrar":
    if not st.session_state.autenticado:
        st.title("📝 REGISTRO DE PACIENTE")
        st.warning("🔒 Debes iniciar sesión para registrar pacientes.")
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown("#### 🔐 Iniciar sesión")

        with st.form("form_login_reg"):
            usuario = st.text_input("👤 Usuario")
            clave   = st.text_input("🔑 Contraseña", type="password")
            entrar  = st.form_submit_button("INGRESAR", use_container_width=True)

            if entrar:
                if usuario in USUARIOS and USUARIOS[usuario] == _hash(clave):
                    st.session_state.autenticado    = True
                    st.session_state.usuario_activo = usuario
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos.")

        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.title("📝 REGISTRO DE PACIENTE")
        st.markdown(f"<small>👤 Sesión: <b>{st.session_state.usuario_activo}</b></small>",
                    unsafe_allow_html=True)

        with st.form("f_reg", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                nom  = st.text_input("Nombre Completo")
                tdoc = st.selectbox("Tipo Doc", ["CC", "TI", "CE", "RC"])
                ndoc = st.text_input("Documento")
                cel  = st.text_input("Celular")
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
                    "entry.346175428":  nom,
                    "entry.1650757004": tdoc,
                    "entry.1302424820": ndoc,
                    "entry.1801154005": ed,
                    "entry.1043165037": cel,
                    "entry.1172011247": ep,
                    "entry.162368130":  rh,
                    "entry.346363":     alert,
                    "entry.1892763134": enom,
                    "entry.2011749615": etel,
                }
                try:
                    resp = requests.post(
                        "https://docs.google.com/forms/d/e/1FAIpQLSfH5wFiZ57m530cMju3wOnI1m1AynsK3uAINDTvnvMYkiFLZg/formResponse",
                        data=payload, timeout=10
                    )
                    if resp.status_code in [200, 302]:
                        st.success("✅ Paciente registrado correctamente.")
                        st.cache_data.clear()
                    else:
                        st.error(f"❌ Error al guardar. Código HTTP: {resp.status_code}")
                except Exception as e:
                    st.error(f"❌ Error de conexión: {e}")

# ══════════════════════════════════════════════
# CONSULTA — libre para todos (QR o manual)
# ══════════════════════════════════════════════
elif st.session_state.menu == "Consulta":
    st.title("🔍 CONSULTA CLÍNICA")

    if st.session_state.get("acceso_qr"):
        st.markdown('<div class="badge-qr">📲 Acceso por escaneo QR</div>',
                    unsafe_allow_html=True)

    doc_default = st.session_state.get("doc_precargado", "")
    id_buscado  = st.text_input("Ingrese Documento", value=doc_default)\
                    .strip().split(".")[0].replace(" ", "")

    if id_buscado and df_p is not None:
        paciente = df_p[df_p["ID_KEY"] == id_buscado]
        if not paciente.empty:
            p = paciente.iloc[0]

            def dato(row, claves):
                for col in row.index:
                    if all(k in col for k in claves):
                        return row[col]
                return "No registra"

            nom_emer = dato(p, ["NOMBRE", "CONTACTO", "EMERGENCIA"])
            tel_emer = dato(p, ["TEL",    "CONTACTO", "EMERGENCIA"])
            alertas  = dato(p, ["CONDICIONES", "ESPECIALES"])

            # Tarjeta resumen — siempre visible
            st.markdown(f"""
            <div class="medical-card">
                <h2 style='margin:0;'>👤 {p.get('NOMBRE','No registra')}</h2>
                <p><b>ID:</b> {p.get('DOCUMENTO','No registra')} |
                   <b>EDAD:</b> {p.get('EDAD','No registra')} |
                   <b>RH:</b> {p.get('RH','No registra')}</p>
                <p><b>EPS:</b> {p.get('EPS','No registra')} |
                   <b>CEL:</b> {p.get('CELULAR','No registra')}</p>
                <p><b>⚠️ ALERTAS:</b> {alertas}</p>
                <div class="emergency-box">
                    🚨 EMERGENCIA: {nom_emer} (Tel: {tel_emer})
                </div>
            </div>""", unsafe_allow_html=True)

            h_p = df_h[df_h["ID_KEY"] == id_buscado].sort_index(ascending=False)

            # ── HISTORIA CLÍNICA PDF — visible para TODOS ──────────────────
            st.subheader("📥 Descargas")
            col_pdf, col_carnet = st.columns(2)

            with col_pdf:
                qp = qr_path(id_buscado)
                hpdf = FPDF()
                hpdf.add_page()
                try:
                    lp = logo_path_tmp()
                    hpdf.image(lp, 10, 8, 30); os.unlink(lp)
                except: pass
                try:
                    hpdf.image(qp, x=165, y=8, w=35, h=35)
                    hpdf.set_xy(155, 44)
                    hpdf.set_font("Arial", "I", 7)
                    hpdf.cell(50, 4, "Escanea para ver historial", align="C")
                except: pass
                hpdf.set_xy(40, 10)
                hpdf.set_font("Arial", "B", 14)
                hpdf.cell(120, 10, "Historia Clinica - Tarjeta Vida QR", ln=False, align="C")
                hpdf.ln(22)
                hpdf.set_font("Arial", "I", 8); hpdf.set_text_color(80, 80, 80)
                hpdf.cell(0, 5, f"Enlace: {APP_BASE_URL}?doc={id_buscado}", ln=True, align="C")
                hpdf.set_text_color(0, 0, 0); hpdf.ln(3)
                hpdf.set_fill_color(230, 230, 230)
                hpdf.set_font("Arial", "B", 10)
                hpdf.cell(0, 7, "DATOS DEL PACIENTE", 1, 1, "L", 1)
                hpdf.set_font("Arial", "", 9)
                hpdf.multi_cell(0, 5,
                    f"Nombre: {p.get('NOMBRE')}\n"
                    f"Documento: {p.get('DOCUMENTO')} | Edad: {p.get('EDAD')} | RH: {p.get('RH')}\n"
                    f"EPS: {p.get('EPS')} | Celular: {p.get('CELULAR')}\n"
                    f"Alertas: {alertas}\n"
                    f"CONTACTO EMERGENCIA: {nom_emer} - Tel: {tel_emer}")
                hpdf.ln(5)
                if not h_p.empty:
                    hpdf.set_fill_color(183, 228, 199)
                    hpdf.set_font("Arial", "B", 10)
                    hpdf.cell(0, 7, "HISTORIAL DE EVOLUCIONES", 1, 1, "L", 1)
                    for _, f in h_p.iterrows():
                        hpdf.set_fill_color(245, 245, 245)
                        hpdf.set_font("Arial", "B", 9)
                        hpdf.cell(0, 6, f"FECHA: {f.get('MARCA TEMPORAL')}", 1, 1, "L", 1)
                        hpdf.set_font("Arial", "", 8)
                        hpdf.multi_cell(0, 4,
                            f"MOTIVO: {f.get('3. MOTIVO DE LA CONSULTA')}\n"
                            f"VALORACION: {f.get('2. VALORACIÓN')}\n"
                            f"MEDIDAS: Talla:{f.get('4. TALLA')} | Peso:{f.get('5. PESO')} | TA:{f.get('6. PRESIÓN ARTERIAL')}\n"
                            f"ANTECEDENTES: {f.get('7. ANTECEDENTES MEDICOS')}\n"
                            f"MEDICAMENTOS: {f.get('8. MEDICAMENTOS')}\n"
                            f"LABORATORIOS: {f.get('9. LABORATORIOS - PROCEDIMIENTOS')}\n"
                            f"EPICRISIS: {f.get('10. EPICRISIS')}")
                        hpdf.ln(2)
                try: os.unlink(qp)
                except: pass
                st.download_button("📥 Historia Clínica PDF",
                    hpdf.output(dest="S").encode("latin-1"),
                    f"HC_{id_buscado}.pdf")

            # ── CARNET — solo usuarios autenticados ────────────────────────
            with col_carnet:
                if st.session_state.autenticado:
                    carnet_bytes = generar_carnet(p, alertas, nom_emer, tel_emer)
                    st.download_button("🪪 Carnet VidaQR (imprimible)",
                        carnet_bytes,
                        f"Carnet_VidaQR_{id_buscado}.pdf",
                        mime="application/pdf")
                    st.info("💡 Imprime a tamaño **85.6 × 54 mm** (tarjeta de crédito).", icon="🖨️")
                else:
                    st.markdown("""
                    <div style='background:#fff3cd;padding:14px;border-radius:10px;
                    border:1px solid #ffc107;margin-top:4px;'>
                        🔒 <b>Carnet VidaQR</b><br>
                        <small>Inicia sesión para descargar el carnet imprimible.</small>
                    </div>
                    """, unsafe_allow_html=True)

            # QR en pantalla — siempre visible
            st.markdown("---")
            st.subheader("📱 Código QR del Paciente")
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(qr_bytes(id_buscado),
                         caption="Escanea para abrir la historia clínica", width=200)
            with col2:
                url_pac = f"{APP_BASE_URL}?doc={id_buscado}"
                st.markdown(f"""
                **🔗 Enlace directo:**  
                `{url_pac}`  

                Al escanear este QR se abrirá directamente  
                la historia clínica de **{p.get('NOMBRE', 'el paciente')}**.
                """)

            # ── Nueva evolución — SIN login requerido ──
            st.markdown("---")
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
                        try:
                            resp = requests.post(
                                "https://docs.google.com/forms/d/e/1FAIpQLSeCCQLkQZbbGw_WJPWzYOhZrm6aOgmTQjDsFRD_y4wV6rB8VA/formResponse",
                                data={
                                    "entry.2019369477": id_buscado,
                                    "entry.1088523869": v_val,
                                    "entry.611862537":  v_mot,
                                    "entry.1275746503": v_tal,
                                    "entry.949747647":  v_pes,
                                    "entry.2091389798": v_pre,
                                    "entry.889985940":  v_ant,
                                    "entry.2016051626": v_med,
                                    "entry.882053172":  v_lab,
                                    "entry.616774918":  v_epi,
                                },
                                timeout=10
                            )
                            if resp.status_code in [200, 302]:
                                st.success("✅ Evolución guardada correctamente.")
                                st.cache_data.clear(); st.rerun()
                            else:
                                st.error(f"❌ Error al guardar. Código HTTP: {resp.status_code}")
                        except Exception as e:
                            st.error(f"❌ Error de conexión: {e}")

            # ── Evoluciones — siempre visibles ─────────
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
                        <p style='font-size:.9em;color:#444;border-top:1px solid #eee;padding-top:5px;'>
                            <b>📝 EPICRISIS:</b> {f.get('10. EPICRISIS')}
                        </p>
                    </div>""", unsafe_allow_html=True)
            else:
                st.info("Este paciente no tiene evoluciones registradas aún.")
        else:
            st.warning("⚠️ No se encontró ningún paciente con ese documento.")
