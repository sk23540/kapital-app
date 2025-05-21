
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF

st.title("📈 Kapitalentwicklung mit Zinseszins")

col1, col2 = st.columns(2)
with col1:
    startkapital = st.number_input("Startkapital (€)", min_value=0, value=1100)
    jahresrendite = st.slider("Jährliche Rendite (%)", 0.0, 20.0, 5.0) / 100
    laufzeit_jahre = st.slider("Anlagedauer (Jahre)", 1, 50, 10)
with col2:
    monatliche_einzahlung = st.number_input("Monatliche Einzahlung (€)", min_value=0, value=100)
    inflation = st.slider("Inflation (%) jährlich", 0.0, 10.0, 2.0) / 100
    gebuehren = st.slider("Rendite-Minderung durch Steuern/Gebühren (%)", 0.0, 10.0, 0.0) / 100

zielkapital = st.number_input("🎯 Zielkapital (€) (optional)", min_value=0, value=20000)
inflationsbereinigt = st.checkbox("Kapital inflationsbereinigt anzeigen", value=True)

effektive_rendite = jahresrendite - gebuehren
monate = laufzeit_jahre * 12
monatliche_rendite = (1 + effektive_rendite)**(1/12) - 1

kapital = [startkapital]
kapital_real = [startkapital] if inflationsbereinigt else None
ziel_erreicht_monat = None

for monat in range(1, monate + 1):
    neues_kapital = kapital[-1] * (1 + monatliche_rendite) + monatliche_einzahlung
    kapital.append(neues_kapital)
    if inflationsbereinigt:
        inflationsfaktor = (1 + inflation)**(monat / 12)
        kapital_real.append(neues_kapital / inflationsfaktor)
    if ziel_erreicht_monat is None and neues_kapital >= zielkapital:
        ziel_erreicht_monat = monat

if zielkapital > 0 and ziel_erreicht_monat:
    jahre_erreicht = ziel_erreicht_monat // 12
    monate_erreicht = ziel_erreicht_monat % 12
    st.success(f"🎉 Ziel von {zielkapital:.0f} € erreicht nach {jahre_erreicht} Jahren und {monate_erreicht} Monaten.")
elif zielkapital > 0:
    st.info("📌 Zielkapital innerhalb des Zeitraums nicht erreicht.")

st.subheader("📊 Kapitalentwicklung")
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(kapital, label="Kapital nominal (€)", color='green')
if inflationsbereinigt:
    ax.plot(kapital_real, label="Kapital inflationsbereinigt (€)", linestyle='--', color='orange')
if ziel_erreicht_monat:
    ax.axvline(ziel_erreicht_monat, color='blue', linestyle=':', label='Ziel erreicht')
ax.set_xlabel("Monate")
ax.set_ylabel("Kapital in €")
ax.grid(True)
ax.legend()
st.pyplot(fig)

df = pd.DataFrame({'Monat': list(range(monate + 1)), 'Kapital (€)': kapital})
if inflationsbereinigt:
    df['Kapital inflationsbereinigt (€)'] = kapital_real

st.subheader("📋 Tabelle (letzte 12 Monate)")
st.dataframe(df.tail(12).reset_index(drop=True).style.format("{:.2f}"))

st.subheader("📎 Tabelle als CSV herunterladen")
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("📥 CSV herunterladen", data=csv, file_name='kapitalentwicklung.csv', mime='text/csv')

from fpdf import FPDF
import os

def create_pdf(df, kapitalziel=None):
    pdf = FPDF()
    
    # Schriftart hinzufügen (z. B. DejaVu Sans)
    font_path = "/tmp/DejaVuSans.ttf"
    if not os.path.exists(font_path):
        import requests
        r = requests.get("https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf")
        with open(font_path, "wb") as f:
            f.write(r.content)

    pdf.add_font("DejaVu", "", font_path, uni=True)
    pdf.set_font("DejaVu", "", 12)

    pdf.add_page()
    pdf.cell(200, 10, txt="Kapitalentwicklung (Zinseszins)", ln=True, align='C')
    if kapitalziel:
        pdf.cell(200, 10, txt=f"Zielkapital: {kapitalziel:.2f} €", ln=True, align='C')
    pdf.ln(10)

    col_names = list(df.columns)
    pdf.set_font("DejaVu", "", 10)
    pdf.cell(30, 10, col_names[0], 1)
    for col in col_names[1:]:
        pdf.cell(50, 10, col, 1)
    pdf.ln()

    for i, row in df.tail(12).iterrows():
        pdf.cell(30, 10, str(int(row['Monat'])), 1)
        pdf.cell(50, 10, f"{row['Kapital (€)']:.2f}", 1)
        if 'Kapital inflationsbereinigt (€)' in df.columns:
            pdf.cell(50, 10, f"{row['Kapital inflationsbereinigt (€)']:.2f}", 1)
        pdf.ln()

    from io import BytesIO
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer


st.subheader("📄 Bericht als PDF herunterladen")
pdf_buffer = create_pdf(df, zielkapital)
st.download_button("📤 PDF herunterladen", data=pdf_buffer, file_name="kapitalbericht.pdf", mime="application/pdf")
