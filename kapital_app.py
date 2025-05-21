import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO
import datetime
import locale

# Spracheinstellung
language = st.selectbox("Sprache / Language", ["Deutsch", "English"])

TEXT = {
    "Deutsch": {
        "title": "Kapitalentwicklung mit Zinseszins",
        "startkapital": "Startkapital (€)",
        "monatsrendite": "Monatliche Rendite (%)",
        "monate": "Anzahl Monate",
        "inflation": "Inflation berücksichtigen (ca. 2 % p.a.)",
        "download": "📄 PDF herunterladen",
        "invalid_input": "Bitte gib gültige Werte ein.",
        "kapital_in_euro": "Kapital in €",
        "monat": "Monat",
        "ziel_kapital": "Zielkapital nach {monate} Monaten: {kapital:.2f} €",
        "szenario_titel": "Szenarienvergleich"
    },
    "English": {
        "title": "Compound Interest Capital Growth",
        "startkapital": "Starting Capital (€)",
        "monatsrendite": "Monthly Return (%)",
        "monate": "Number of Months",
        "inflation": "Adjust for inflation (approx. 2% p.a.)",
        "download": "📄 Download PDF",
        "invalid_input": "Please enter valid values.",
        "kapital_in_euro": "Capital in €",
        "monat": "Month",
        "ziel_kapital": "Target capital after {monate} months: {kapital:.2f} €",
        "szenario_titel": "Scenario Comparison"
    }
}
T = TEXT[language]

st.title(T["title"])

# Eingabefelder
startkapital = st.number_input(T["startkapital"], min_value=0.0, value=1000.0, step=100.0)
monatsrendite = st.number_input(T["monatsrendite"], min_value=0.0, max_value=100.0, value=27.27)
monate = st.slider(T["monate"], min_value=1, max_value=100, value=12)
inflation_anpassen = st.checkbox(T["inflation"])

# Rendite in Dezimal umrechnen
monatsrendite /= 100
inflationsrate = 0.00165 if inflation_anpassen else 0

# Funktion zur Kapitalberechnung
def berechne_kapital(start, rendite, monate, inflationsrate=0.0):
    kapital = [start]
    for i in range(1, monate + 1):
        neues = kapital[-1] * (1 + rendite - inflationsrate)
        kapital.append(neues)
    return kapital

# Hauptszenario
kapitalentwicklung = berechne_kapital(startkapital, monatsrendite, monate, inflationsrate)
monatsliste = list(range(0, monate + 1))

# Szenarienvergleich
szenarien = [0.10, 0.20, 0.2727]
plt.figure(figsize=(10, 6))
for r in szenarien:
    daten = berechne_kapital(startkapital, r, monate, inflationsrate)
    plt.plot(monatsliste, daten, marker='o', label=f"{round(r*100, 2)}%")
plt.xlabel(T["monat"])
plt.ylabel(T["kapital_in_euro"])
plt.title(T["szenario_titel"])
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("chart.png")  # Für PDF später

# Tabelle anzeigen
df = pd.DataFrame({
    T["monat"]: monatsliste,
    T["kapital_in_euro"]: [round(k, 2) for k in kapitalentwicklung]
})
st.line_chart(df.set_index(T["monat"]))

zielkapital = kapitalentwicklung[-1]
st.success(T["ziel_kapital"].format(monate=monate, kapital=zielkapital))

# PDF-Export
def create_pdf(df, zielkapital):
    pdf = FPDF()
    pdf.add_page()
    font_path = "DejaVuSans.ttf"
    pdf.add_font("DejaVu", "", font_path, uni=True)
    pdf.set_font("DejaVu", "", 14)
    pdf.cell(200, 10, txt=T["title"], ln=True)
    pdf.set_font("DejaVu", "", 12)
    pdf.cell(200, 10, txt=T["ziel_kapital"].format(monate=monate, kapital=zielkapital), ln=True)

    pdf.image("chart.png", x=10, y=30, w=180)

    pdf.ln(85)
    for index, row in df.iterrows():
        pdf.cell(100, 8, f"{T['monat']} {row[T['monat']]}: {row[T['kapital_in_euro']]} €", ln=True)

    buffer = BytesIO()
    pdf_bytes = pdf.output(dest="S").encode("latin1")
    buffer.write(pdf_bytes)
    buffer.seek(0)
    return buffer

pdf_buffer = create_pdf(df, zielkapital)

# Download-Button
dateiname = f"Kapitalentwicklung_M{monate}.pdf"
st.download_button(
    label=T["download"],
    data=pdf_buffer,
    file_name=dateiname,
    mime="application/pdf"
)
