from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import requests

app = Flask(__name__)

# =========================
# KONFIGURASI AI (GEMINI)
# =========================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("❌ GEMINI_API_KEY belum diset di environment")

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-pro:generateContent?key=" + GEMINI_API_KEY
)

# =========================
# STANDAR KUALITAS AIR
# =========================
PH_MIN, PH_MAX = 6.5, 8.5
TDS_MAX = 500
EC_MAX = 1000

# =========================
# STATUS AIR
# =========================
def status_air(pH, EC, TDS):
    try:
        pH = float(pH)
        EC = float(EC)
        TDS = float(TDS)
    except:
        return "DATA ERROR", "badge-gray", "Data tidak valid."

    if PH_MIN <= pH <= PH_MAX and EC <= EC_MAX and TDS <= TDS_MAX:
        return "AMAN", "badge-green", "Air layak digunakan."
    elif pH < PH_MIN:
        return "ASAM", "badge-red", "Air bersifat asam."
    elif pH > PH_MAX:
        return "BASA", "badge-red", "Air bersifat basa."
    else:
        return "WASPADA", "badge-orange", "Perlu pengolahan sederhana."

# =========================
# LOAD CSV
# =========================
def load_data():
    path = os.path.join(os.path.dirname(__file__), "air.csv")
    if not os.path.exists(path):
        raise FileNotFoundError("air.csv tidak ditemukan")
    return pd.read_csv(path)

# =========================
# DASHBOARD
# =========================
@app.route("/")
def index():
    df = load_data()
    hasil = []

    for _, row in df.iterrows():
        status, warna, pesan = status_air(row["pH"], row["EC"], row["TDS"])
        hasil.append({
            "rumah": row["Rumah"],
            "pH": row["pH"],
            "EC": row["EC"],
            "TDS": row["TDS"],
            "status": status,
            "warna": warna,
            "pesan": pesan
        })

    return render_template("indexx.html", data=hasil)

# =========================
# 🤖 AI CHAT (GEMINI)
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message", "").strip()
    if not user_msg:
        return jsonify({"reply": "Silakan masukkan pertanyaan."})

    df = load_data()
    summary = df[["Rumah", "pH", "EC", "TDS"]].to_string(index=False)

    prompt = f"""
Kamu adalah AI ahli kualitas air tanah.

Data kualitas air Cileles:
{summary}

Pertanyaan warga:
{user_msg}

Jawab singkat, jelas, dan mudah dipahami masyarakat.
"""

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(GEMINI_URL, json=payload, timeout=30)
        response.raise_for_status()

        data = response.json()
        reply = data["candidates"][0]["content"]["parts"][0]["text"]

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({
            "reply": "⚠️ AI sedang tidak tersedia. Coba lagi nanti."
        })

# =========================
# PETA
# =========================
@app.route("/peta")
def peta():
    df = load_data()
    lokasi = []

    for _, row in df.iterrows():
        status, _, _ = status_air(row["pH"], row["EC"], row["TDS"])
        lokasi.append({
            "rumah": row["Rumah"],
            "lat": row["Latitude"],
            "lon": row["Longitude"],
            "status": status
        })

    return render_template("peta.html", lokasi=lokasi)

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
