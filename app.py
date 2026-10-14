import streamlit as st
from PIL import Image
import json
import io
import os
from google import genai
from google.genai import types
from xhtml2pdf import pisa

st.set_page_config(
    page_title="TikTok Growth Engine & Auditor",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Injeksi CSS Khusus Desain Mobile Modern & Aksen TikTok
st.markdown("""
<style>
    /* Global Container */
    .main {
        background: linear-gradient(180deg, #0b0f19 0%, #111827 100%);
        color: #f8fafc;
    }
    
    /* Header Card */
    .hero-container {
        background: linear-gradient(135deg, rgba(254, 44, 85, 0.12) 0%, rgba(0, 242, 254, 0.12) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px 18px;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
        text-align: center;
    }
    .hero-title {
        font-size: 1.45rem;
        font-weight: 800;
        background: linear-gradient(90deg, #fe2c55, #00f2fe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 6px;
    }
    .hero-subtitle {
        color: #94a3b8;
        font-size: 0.85rem;
        line-height: 1.4;
    }
    
    /* Kartu Metrik Mobile */
    .glass-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 14px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    .card-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #f1f5f9;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    /* Highlight Formula Traffic */
    .traffic-pill {
        background: rgba(0, 242, 254, 0.08);
        border-left: 3px solid #00f2fe;
        border-radius: 0 8px 8px 0;
        padding: 10px 12px;
        margin-bottom: 10px;
        font-size: 0.85rem;
        color: #e2e8f0;
    }
    
    .traffic-pill b {
        color: #38bdf8;
    }
    
    /* Live Formula */
    .live-pill {
        background: rgba(254, 44, 85, 0.08);
        border-left: 3px solid #fe2c55;
        border-radius: 0 8px 8px 0;
        padding: 10px 12px;
        margin-bottom: 10px;
        font-size: 0.85rem;
        color: #e2e8f0;
    }
    
    .live-pill b {
        color: #fb7185;
    }

    /* Fast Action Steps */
    .action-step-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(244, 63, 94, 0.25);
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 8px;
        font-size: 0.85rem;
        color: #fca5a5;
    }

    /* Tombol Streamlit Mobile */
    .stButton>button {
        background: linear-gradient(90deg, #fe2c55 0%, #ff0050 50%, #00f2fe 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-size: 0.95rem !important;
        box-shadow: 0 4px 15px rgba(254, 44, 85, 0.35) !important;
        transition: all 0.3s ease !important;
    }
</style>
""", unsafe_allow_html=True)

# Fungsi Generator PDF
def generate_pdf_report(data, tiktok_url):
    status_text = data.get("shadowban", {}).get("status", "-")
    badge_bg = "#dcfce7" if "Aman" in status_text else ("#fee2e2" if "Shadowban" in status_text else "#fef3c7")
    badge_color = "#166534" if "Aman" in status_text else ("#991b1b" if "Shadowban" in status_text else "#92400e")

    profil_rows = []
    for item in data.get("profil_audit", []):
        el = str(item.get("elemen", "-"))
        ms = str(item.get("masalah", "-"))
        sl = str(item.get("solusi_langsung", "-"))
        profil_rows.append(
            '<div style="background-color:#f8fafc; border-left:3px solid #3b82f6; padding:5px 8px; margin-bottom:4px; font-size:8pt;">'
            + '<b>' + el + ':</b><br>'
            + '<span style="color:#b91c1c;">Masalah:</span> ' + ms + '<br>'
            + '<span style="color:#15803d;">Solusi:</span> ' + sl
            + '</div>'
        )
    profil_html = "".join(profil_rows)

    killers_rows = []
    for tk in data.get("traffic_killers", []):
        fk = str(tk.get("faktor", "-"))
        dp = str(tk.get("dampak_algoritma", "-"))
        killers_rows.append(
            '<div style="background-color:#fef2f2; border-left:3px solid #ef4444; padding:5px 8px; margin-bottom:4px; font-size:8pt;">'
            + '<b>Faktor:</b> ' + fk + '<br>'
            + '<b>Dampak:</b> ' + dp
            + '</div>'
        )
    killers_html = "".join(killers_rows)

    v_cadence = data.get("video_cadence_formula", {})
    l_cadence = data.get("live_streaming_formula", {})
    ratecard = data.get("ratecard_valuation", {})
    growth = data.get("traffic_growth_recipe", {})
    niche = data.get("niche_blueprint", {})
    fast_actions = data.get("fast_action_72h", [])

    act1 = fast_actions[0] if len(fast_actions) > 0 else "-"
    act2 = fast_actions[1] if len(fast_actions) > 1 else "-"
    act3 = fast_actions[2] if len(fast_actions) > 2 else "-"

    html_pieces = [
        "<!DOCTYPE html><html><head><meta charset='utf-8'><style>",
        "@page { size: A4 portrait; margin: 12mm 10mm 12mm 10mm; }",
        "body { font-family: Helvetica, Arial, sans-serif; color: #0f172a; line-height: 1.35; font-size: 8pt; }",
        ".header-table { width: 100%; border-bottom: 2px solid #0f172a; padding-bottom: 4px; margin-bottom: 8px; }",
        ".title { font-size: 14pt; font-weight: bold; color: #0f172a; }",
        ".metric-table { width: 100%; margin-bottom: 10px; }",
        ".metric-box { background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 4px; padding: 6px; text-align: center; }",
        ".metric-number { font-size: 14pt; font-weight: bold; color: #2563eb; }",
        ".badge { padding: 2px 6px; border-radius: 3px; font-weight: bold; font-size: 7pt; }",
        ".section-title { font-size: 9.5pt; font-weight: bold; color: #0f172a; border-bottom: 1px solid #cbd5e1; padding-bottom: 2px; margin-top: 8px; margin-bottom: 5px; }",
        ".cadence-box { background-color: #eff6ff; border: 1px solid #bfdbfe; border-radius: 4px; padding: 6px 8px; margin-bottom: 6px; }",
        ".rate-box { background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 4px; padding: 6px 8px; margin-bottom: 5px; }",
        ".quote-box { background-color: #f1f5f9; border-left: 3px solid #64748b; padding: 4px 6px; margin-top: 3px; margin-bottom: 3px; font-style: italic; font-size: 7.5pt; }",
        ".footer-note { margin-top: 10px; text-align: center; font-size: 6.5pt; color: #94a3b8; border-top: 1px dashed #cbd5e1; padding-top: 4px; }",
        "</style></head><body>",
        "<table class='header-table'><tr>",
        "<td><div class='title'>TIKTOK SYSTEMIC DIAGNOSTIC & GROWTH REPORT</div><div style='font-size: 7.5pt; color: #64748b;'>Audit Algoritma, Formula Ritme Konten, Live Streaming & Valuasi Ratecard</div></td>",
        "<td style='text-align: right; vertical-align: bottom;'><div style='font-size: 7pt; color: #475569;'>Target Akun: <b>" + str(tiktok_url) + "</b></div></td>",
        "</tr></table>",
        "<table class='metric-table'><tr>",
        "<td width='30%' style='padding-right: 4px;'><div class='metric-box'><div style='font-size: 6pt; color: #64748b; font-weight: bold;'>KESEHATAN PROFIL</div><div class='metric-number'>" + str(data.get('health_score', 0)) + "<span style='font-size: 7.5pt; color: #94a3b8;'>/100</span></div></div></td>",
        "<td width='35%' style='padding-right: 4px;'><div class='metric-box'><div style='font-size: 6pt; color: #64748b; font-weight: bold;'>STATUS ALGORITMA</div><div style='margin-top: 2px;'><span class='badge' style='background-color: " + badge_bg + "; color: " + badge_color + ";'>" + str(status_text) + "</span></div></div></td>",
        "<td width='35%'><div class='metric-box'><div style='font-size: 6pt; color: #64748b; font-weight: bold;'>NICHE UTAMA</div><div style='font-size: 8pt; font-weight: bold; color: #0f172a; margin-top: 2px;'>" + str(niche.get('primary_niche', '-')) + "</div></div></td>",
        "</tr></table>",
        "<div class='section-title'>🧪 RESEP & FORMULA EKSEKUSI UP TRAFFIC</div>",
        "<div class='cadence-box'><table width='100%'><tr>",
        "<td width='50%' style='vertical-align: top; padding-right: 4px;'>",
        "<b style='color: #1d4ed8; font-size: 8.5pt;'>📹 Resep Video VT Harian:</b><br>",
        "• <b>Kuantitas Upload:</b> " + str(v_cadence.get('quantity_per_day', '-')) + "<br>",
        "• <b>Durasi Optimal:</b> " + str(v_cadence.get('target_duration_seconds', '-')) + "<br>",
        "• <b>Jam Tayang Terbaik:</b> " + str(v_cadence.get('best_posting_hours', '-')) + "<br>",
        "• <b>Alasan Ritme:</b> <span style='font-size: 7pt; color: #475569;'>" + str(v_cadence.get('cadence_reasoning', '-')) + "</span>",
        "</td>",
        "<td width='50%' style='vertical-align: top; padding-left: 4px; border-left: 1px dashed #bfdbfe;'>",
        "<b style='color: #1d4ed8; font-size: 8.5pt;'>🎙️ Resep Sesi Live Streaming:</b><br>",
        "• <b>Frekuensi Sesi:</b> " + str(l_cadence.get('frequency_per_day', '-')) + "<br>",
        "• <b>Rentang Durasi:</b> Min " + str(l_cadence.get('min_duration_hours', '-')) + " s/d Max " + str(l_cadence.get('max_duration_hours', '-')) + "<br>",
        "• <b>Jam Prime Time Live:</b> " + str(l_cadence.get('prime_time_hours', '-')) + "<br>",
        "• <b>Format Live:</b> <span style='font-size: 7pt; color: #475569;'>" + str(niche.get('live_monetization', '-')) + "</span>",
        "</td></tr></table></div>",
        "<div style='background-color:#f8fafc; border-left:3px solid #3b82f6; padding:5px 8px; margin-bottom:5px; font-size:7.5pt;'>",
        "<b>Formula Hook (Detik 0 - 3):</b><div class='quote-box'>\"" + str(growth.get('hook_first_3s', '-')) + "\"</div>",
        "<b>Struktur Retensi:</b> " + str(growth.get('retention_structure', '-')),
        "</div>",
        "<div class='section-title'>🚨 PROTOKOL PEMULIHAN CEPAT (72 JAM)</div>",
        "<div style='background-color:#fef2f2; border-left:3px solid #ef4444; padding:4px 6px; margin-bottom:3px; font-size:7.5pt;'><b>Hari ke-1:</b> " + str(act1) + "</div>",
        "<div style='background-color:#fef2f2; border-left:3px solid #ef4444; padding:4px 6px; margin-bottom:3px; font-size:7.5pt;'><b>Hari ke-2:</b> " + str(act2) + "</div>",
        "<div style='background-color:#fef2f2; border-left:3px solid #ef4444; padding:4px 6px; margin-bottom:3px; font-size:7.5pt;'><b>Hari ke-3:</b> " + str(act3) + "</div>",
        "<div class='section-title'>⚠️ TEMUAN KEKURANGAN PROFIL & TRAFFIC KILLER</div>",
        "<table width='100%'><tr>",
        "<td width='50%' style='vertical-align: top; padding-right: 4px;'><div style='font-size: 7.5pt; font-weight: bold; margin-bottom: 2px;'>Kelemahan Profil & Visual:</div>" + profil_html + "</td>",
        "<td width='50%' style='vertical-align: top; padding-left: 4px;'><div style='font-size: 7.5pt; font-weight: bold; margin-bottom: 2px;'>Pemicu Anjloknya Distribusi FYP:</div>" + killers_html + "</td>",
        "</tr></table>",
        "<div class='section-title'>💰 PENILAIAN STANDAR RATECARD ENDORSEMENT</div>",
        "<div class='rate-box'><table width='100%'><tr>",
        "<td width='33%'><b>Video Feed (VT):</b><br><span style='color:#15803d; font-weight:bold;'>" + str(ratecard.get('video_feed', '-')) + "</span></td>",
        "<td width='33%'><b>Live / Jam:</b><br><span style='color:#15803d; font-weight:bold;'>" + str(ratecard.get('live_session_per_hour', '-')) + "</span></td>",
        "<td width='34%'><b>Paket Bundle:</b><br><span style='color:#15803d; font-weight:bold;'>" + str(ratecard.get('bundle_package', '-')) + "</span></td>",
        "</tr></table><div style='font-size: 7pt; color: #475569; margin-top: 3px; border-top: 1px dashed #bbf7d0; padding-top: 2px;'>",
        "<b>Brand-Fit Cocok:</b> " + str(ratecard.get('suitable_brand_categories', '-')) + "<br>",
        "<b>Dasar Negosiasi:</b> " + str(ratecard.get('valuation_rationale', '-')),
        "</div></div>",
        "<div class='footer-note'>Laporan dibuat otomatis dengan AI Multi-Modal Engine. Estimasi ratecard bersifat acuan standar pasar agensi kreator.</div>",
        "</body></html>"
    ]

    html_content = "".join(html_pieces)
    pdf_buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)
    if pisa_status.err:
        return None
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()

# Sidebar Pengaturan
st.sidebar.markdown("### ⚙️ Pengaturan Mesin")
api_key = st.sidebar.text_input(
    "Gemini API Key:", 
    type="password", 
    help="Dapatkan dari Google AI Studio"
)
st.sidebar.caption("Gunakan API key yang valid untuk menjalankan engine analitik.")

# Hero Header Visual
st.markdown("""
<div class="hero-container">
    <div style="font-size: 2rem; margin-bottom: 4px;">⚡ 📊</div>
    <div class="hero-title">TikTok Diagnostic & Growth Engine</div>
    <div class="hero-subtitle">Audit algoritma komprehensif, resep pemulihan traffic FYP, formula live, dan standar valuasi ratecard agensi.</div>
</div>
""", unsafe_allow_html=True)

# Input Section Khusus Layar Ponsel
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
st.markdown("<div class='card-title'>🎯 Profil & Target Akun</div>", unsafe_allow_html=True)
tiktok_url = st.text_input("Link Profil TikTok:", placeholder="https://www.tiktok.com/@username", label_visibility="collapsed")

profile_img = st.file_uploader(
    "1. Screenshot Profil Akun (Wajib):", 
    type=["jpg", "jpeg", "png"],
    help="Pastikan bio, followers, total like, dan views video terlihat jelas."
)

analytics_img = st.file_uploader(
    "2. Screenshot Creator Tools / FYP Traffic (Opsional):", 
    type=["jpg", "jpeg", "png"],
    help="Opsional tapi sangat direkomendasikan untuk akurasi analitik 100%."
)
st.markdown("</div>", unsafe_allow_html=True)

if st.button("🚀 JALANKAN DEEP DIAGNOSTIC", use_container_width=True):
    if not api_key:
        st.error("Silakan masukkan Gemini API Key terlebih dahulu di menu samping (Sidebar).")
    elif not tiktok_url or not profile_img:
        st.warning("Mohon isi link akun dan unggah screenshot profil utama terlebih dahulu.")
    else:
        with st.spinner("Sedang membedah matriks engagement, ritme konten, dan valuasi ratecard..."):
            try:
                prompt_path = os.path.join(os.path.dirname(__file__), "prompt.txt")
                if not os.path.exists(prompt_path):
                    st.error("File prompt.txt tidak ditemukan di direktori!")
                    st.stop()

                with open(prompt_path, "r", encoding="utf-8") as f:
                    raw_prompt = f.read()

                client = genai.Client(api_key=api_key)
                img_profile = Image.open(profile_img)
                content_inputs = [img_profile]

                analytics_context = "TIDAK DILAMPIRKAN. Nilai drop traffic dari fluktuasi angka views di grid."
                if analytics_img:
                    img_analytics = Image.open(analytics_img)
                    content_inputs.append(img_analytics)
                    analytics_context = "DILAMPIRKAN. Bedah grafik views, rasio FYP, dan retensi penonton secara komprehensif."

                deep_prompt = raw_prompt.replace("__URL__", str(tiktok_url)).replace("__ANALYTICS__", analytics_context)
                content_inputs.append(deep_prompt)

                models_to_try = [
                    "gemini-3.8-flash",
                    "gemini-3.5-flash",
                    "gemini-3.1-flash-lite"
                ]
                response = None
                last_err = None

                for mdl in models_to_try:
                    try:
                        response = client.models.generate_content(
                            model=mdl,
                            contents=content_inputs,
                            config=types.GenerateContentConfig(
                                response_mime_type="application/json"
                            )
                        )
                        if response and response.text:
                            break
                    except Exception as err:
                        last_err = err
                        continue

                if not response or not response.text:
                    raise last_err if last_err else Exception("Gagal mendapatkan respons.")

                data = json.loads(response.text)

                # ================= 1. TOMBOL DOWNLOAD PDF (DI ATAS) =================
                pdf_data = generate_pdf_report(data, tiktok_url)
                if pdf_data:
                    username_clean = tiktok_url.replace("https://www.tiktok.com/@", "").replace("/", "").split("?")[0]
                    file_label = f"Audit_TikTok_{username_clean}.pdf" if username_clean else "Audit_TikTok_Report.pdf"
                    st.download_button(
                        label="📥 DOWNLOAD DOKUMEN LAPORAN LENGKAP (PDF)",
                        data=pdf_data,
                        file_name=file_label,
                        mime="application/pdf",
                        use_container_width=True
                    )

                # ================= 2. RINGKASAN METRIK =================
                st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                st.markdown("<div class='card-title'>📊 Ringkasan Diagnostik Akun</div>", unsafe_allow_html=True)
                
                col_score, col_stat = st.columns(2)
                with col_score:
                    st.metric("Skor Kesehatan", f"{data['health_score']}/100")
                with col_stat:
                    st.metric("Status Akun", data['shadowban']['status'])
                
                st.caption(f"**Akar Masalah:** {data['shadowban']['akar_masalah']}")
                st.markdown(f"**Niche Terdeteksi:** `{data['niche_blueprint']['primary_niche']}`")
                st.markdown("</div>", unsafe_allow_html=True)

                # ================= 3. RESEP RITME TRAFFIC =================
                st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                st.markdown("<div class='card-title'>💊 Formula Obat Kuat Up Traffic</div>", unsafe_allow_html=True)
                
                v = data['video_cadence_formula']
                st.markdown(f"""
                <div class="traffic-pill">
                    <b>📹 RESEP VIDEO VT HARIAN</b><br>
                    • <b>Kuantitas Upload:</b> {v['quantity_per_day']}<br>
                    • <b>Target Durasi Video:</b> {v['target_duration_seconds']}<br>
                    • <b>Jam Tayang Optimal:</b> {v['best_posting_hours']}<br>
                    <span style="font-size:0.75rem; color:#94a3b8;">{v['cadence_reasoning']}</span>
                </div>
                """, unsafe_allow_html=True)

                l = data['live_streaming_formula']
                st.markdown(f"""
                <div class="live-pill">
                    <b>🎙️ RESEP LIVE STREAMING</b><br>
                    • <b>Frekuensi:</b> {l['frequency_per_day']}<br>
                    • <b>Rentang Durasi:</b> Min {l['min_duration_hours']} s/d Max {l['max_duration_hours']}<br>
                    • <b>Jam Prime Time:</b> {l['prime_time_hours']}<br>
                    • <b>Kunci Retensi:</b> {l['live_retention_tip']}
                </div>
                """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

                # ================= 4. PROTOKOL 72 JAM =================
                st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                st.markdown("<div class='card-title'>🚨 Protokol Pemulihan Cepat (72 Jam)</div>", unsafe_allow_html=True)
                for idx, step in enumerate(data['fast_action_72h'][:3]):
                    st.markdown(f"""
                    <div class="action-step-card">
                        <b>Hari ke-{idx+1}:</b> {step}
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

                # ================= 5. FORMULA HOOK =================
                st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                st.markdown("<div class='card-title'>🪝 Formula Hook & Struktur Retensi</div>", unsafe_allow_html=True)
                st.info(f"**Hook 0-3 Detik Pertama:**\n\n> {data['traffic_growth_recipe']['hook_first_3s']}")
                st.markdown(f"**Struktur Retensi:**\n\n{data['traffic_growth_recipe']['retention_structure']}")
                st.markdown("</div>", unsafe_allow_html=True)

                # ================= 6. VALUASI RATECARD ENDORSEMENT =================
                st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                st.markdown("<div class='card-title'>💰 Standar Valuasi Ratecard Endorsement</div>", unsafe_allow_html=True)
                rc = data['ratecard_valuation']
                
                c_rc1, c_rc2 = st.columns(2)
                with c_rc1:
                    st.success(f"**Video Feed (VT):**\n\n{rc['video_feed']}")
                with c_rc2:
                    st.info(f"**Live / Jam:**\n\n{rc['live_session_per_hour']}")
                
                st.warning(f"**Paket Bundle Campaign:** {rc['bundle_package']}")
                st.markdown(f"🛍️ **Kategori Brand Cocok:** `{rc['suitable_brand_categories']}`")
                st.caption(f"📌 **Dasar Valuasi:** {rc['valuation_rationale']}")
                st.markdown("</div>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Gagal memproses analisis: {e}")
