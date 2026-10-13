import streamlit as st
from PIL import Image
import json
import io
import os
from google import genai
from google.genai import types
from xhtml2pdf import pisa

st.set_page_config(
    page_title="TikTok Systemic Auditor & Growth Engine",
    page_icon="⚡",
    layout="wide"
)

# Generator PDF
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

# Sidebar
api_key = st.sidebar.text_input(
    "Gemini API Key:", 
    type="password", 
    help="Dapatkan di Google AI Studio (aistudio.google.com)"
)
st.sidebar.markdown("---")
st.sidebar.info("💡 **Tips Akurasi:**\nUnggah screenshot profil dan analitik Creator Tools agar audit presisi.")

# Main Interface
st.title("⚡ TikTok Deep Diagnostic & Growth Engine")
st.caption("Bedah algoritma akun, resep kuantitas video & durasi, jadwal live streaming, dan ratecard endorsement.")

col1, col2 = st.columns(2)
with col1:
    tiktok_url = st.text_input("Link Profil TikTok:", placeholder="https://www.tiktok.com/@username")
    profile_img = st.file_uploader(
        "1. Screenshot Halaman Profil (Wajib):", 
        type=["jpg", "jpeg", "png"],
        help="Pastikan bio, follower, total like, dan views terlihat jelas."
    )
with col2:
    st.write("")
    st.write("")
    analytics_img = st.file_uploader(
        "2. Screenshot Analitik / Creator Tools (Opsional):", 
        type=["jpg", "jpeg", "png"],
        help="Unggah grafik views atau sumber traffic FYP."
    )

if st.button("Jalankan Deep Diagnostic", type="primary", use_container_width=True):
    if not api_key:
        st.error("Silakan masukkan Gemini API Key terlebih dahulu di menu samping.")
    elif not tiktok_url or not profile_img:
        st.warning("Mohon cantumkan link akun dan unggah screenshot profil utama.")
    else:
        with st.spinner("Sedang membedah matriks engagement, ritme konten, dan valuasi ratecard..."):
            try:
                # Baca prompt dari file prompt.txt
                prompt_path = os.path.join(os.path.dirname(__file__), "prompt.txt")
                if not os.path.exists(prompt_path):
                    st.error("File prompt.txt tidak ditemukan di folder yang sama!")
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

                models_to_try = ["gemini-3.8-flash", "gemini-2.5-flash"]
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

                st.divider()

                # Tombol Download PDF
                st.subheader("📥 Download Dokumen Laporan")
                pdf_data = generate_pdf_report(data, tiktok_url)
                if pdf_data:
                    username_clean = tiktok_url.replace("https://www.tiktok.com/@", "").replace("/", "").split("?")[0]
                    file_label = f"Audit_TikTok_{username_clean}.pdf" if username_clean else "Audit_TikTok_Report.pdf"
                    st.download_button(
                        label="📄 KLIK DI SINI UNTUK DOWNLOAD LAPORAN PDF",
                        data=pdf_data,
                        file_name=file_label,
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True
                    )
                else:
                    st.warning("Pustaka PDF (xhtml2pdf) sedang terkendala rendering.")

                st.divider()

                # 1. Ringkasan Metrik
                c_score, c_sb, c_niche = st.columns([1, 1.2, 1.2])
                with c_score:
                    st.metric("Skor Kesehatan Akun", f"{data['health_score']}/100")
                    st.progress(data['health_score'] / 100)
                
                with c_sb:
                    st.metric("Status Algoritma", data['shadowban']['status'])
                    st.caption(data['shadowban']['akar_masalah'])

                with c_niche:
                    st.metric("Niche Utama", data['niche_blueprint']['primary_niche'])
                    st.caption(f"Target: {data['niche_blueprint']['target_audience']}")

                st.divider()

                # 2. Resep Video & Live
                st.subheader("💊 Obat Kuat Up Traffic (Formula Ritme & Durasi)")
                col_v, col_l = st.columns(2)
                with col_v:
                    st.info(f"**📹 Resep Video VT Harian:**\n\n"
                            f"• **Kuantitas Posting:** `{data['video_cadence_formula']['quantity_per_day']}`\n\n"
                            f"• **Durasi Optimal:** `{data['video_cadence_formula']['target_duration_seconds']}`\n\n"
                            f"• **Jam Upload Terbaik:** `{data['video_cadence_formula']['best_posting_hours']}`\n\n"
                            f"• **Alasan:** {data['video_cadence_formula']['cadence_reasoning']}")

                with col_l:
                    st.success(f"**🎙️ Resep Sesi Live Streaming:**\n\n"
                               f"• **Frekuensi:** `{data['live_streaming_formula']['frequency_per_day']}`\n\n"
                               f"• **Durasi:** Min **{data['live_streaming_formula']['min_duration_hours']}** — Max **{data['live_streaming_formula']['max_duration_hours']}**\n\n"
                               f"• **Prime Time:** `{data['live_streaming_formula']['prime_time_hours']}`\n\n"
                               f"• **Kunci Retensi:** {data['live_streaming_formula']['live_retention_tip']}")

                st.divider()

                # 3. Protokol Darurat 72 Jam
                st.subheader("🚨 Tindakan Darurat Cepat (Protokol Pemulihan 72 Jam)")
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.error(f"**Hari ke-1:**\n\n{data['fast_action_72h'][0]}")
                with c2:
                    st.warning(f"**Hari ke-2:**\n\n{data['fast_action_72h'][1]}")
                with c3:
                    st.info(f"**Hari ke-3:**\n\n{data['fast_action_72h'][2]}")

                st.divider()

                # 4. Audit Profil & Traffic Killers
                col_kiri, col_kanan = st.columns(2)
                with col_kiri:
                    st.subheader("⚠️ Audit Kekurangan Profil & Visual")
                    for item in data['profil_audit']:
                        with st.expander(f"📌 {item['elemen']}", expanded=True):
                            st.write(f"❌ **Kelemahan:** {item['masalah']}")
                            st.write(f"✅ **Solusi Perbaikan:** {item['solusi_langsung']}")

                with col_kanan:
                    st.subheader("📉 Traffic Killer (Pemicu Drop Views)")
                    for tk in data['traffic_killers']:
                        st.warning(f"**Faktor:** {tk['faktor']}\n\n**Dampak:** {tk['dampak_algoritma']}")

                st.divider()

                # 5. Formula Hook
                st.subheader("🧪 Cetak Biru Hook & Retensi Video")
                st.info(f"**Formula Hook (3 Detik Pertama):**\n\n> {data['traffic_growth_recipe']['hook_first_3s']}\n\n"
                        f"**Struktur Penahan Retensi:**\n\n{data['traffic_growth_recipe']['retention_structure']}")

                st.divider()

                # 6. Valuasi Ratecard (Paling Bawah)
                st.subheader("💰 Standar Valuasi Ratecard Endorsement")
                rc1, rc2, rc3 = st.columns(3)
                with rc1:
                    st.success(f"**Video Feed (VT):**\n\n### {data['ratecard_valuation']['video_feed']}")
                with rc2:
                    st.info(f"**Live Streaming (Per Jam):**\n\n### {data['ratecard_valuation']['live_session_per_hour']}")
                with rc3:
                    st.warning(f"**Paket Bundle Campaign:**\n\n### {data['ratecard_valuation']['bundle_package']}")

                st.write(f"🛍️ **Kategori Brand Cocok:** `{data['ratecard_valuation']['suitable_brand_categories']}`")
                st.caption(f"📌 **Dasar Valuasi Negosiasi:** {data['ratecard_valuation']['valuation_rationale']}")

            except Exception as e:
                st.error(f"Gagal memproses analisis: {e}")