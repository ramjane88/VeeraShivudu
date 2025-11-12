import os, json, time, tempfile
from flask import Flask, request, jsonify, send_file, render_template_string
from dotenv import load_dotenv
from prompts import POST_SYSTEM
from llm_adapter import call_llm
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")   # optional default key
ADMIN_PASS = os.getenv("ADMIN_PASS", "change_this")

app = Flask(__name__)

INDEX_HTML = """
<!doctype html>
<title>VeeraShivudu (demo)</title>
<h2>VeeraShivudu — Demo</h2>
<p>Use POST /api/generate/1 with text or audio. This is a minimal demo endpoint.</p>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(INDEX_HTML)

def build_messages(system_prompt, user_text):
    return [
        {"role":"system","content": system_prompt},
        {"role":"user","content": user_text}
    ]

@app.route("/api/generate/<int:business_id>", methods=["POST"])
def generate(business_id):
    # protect: does not require admin for simple generate
    # Accept user API key in header X-USER-KEY (optional)
    user_key = request.headers.get("X-USER-KEY") or request.form.get("user_key")
    provider = (request.headers.get("X-LLM-PROVIDER") or request.form.get("provider") or "openai").lower()
    api_key = user_key if user_key else OPENAI_API_KEY
    if not api_key:
        return jsonify({"error":"No API key provided (set OPENAI_API_KEY in Vercel or send X-USER-KEY header)"}), 400

    # minimal business info (in real app load from DB)
    business = {
      "name": "Demo Shop",
      "category": "Kirana",
      "city": "YourCity",
      "tone": "friendly"
    }
    text = (request.form.get("text") or "").strip()
    if not text:
        return jsonify({"error":"Provide text in form field 'text' or audio (not implemented in minimal demo)"}), 400

    user_prompt = f\"\"\"business_name: {business['name']}
category: {business['category']}
city: {business['city']}
tone: {business['tone']}
offer_description: {text}
audience: local customers
language_hint: auto
Generate 3 variants in strict JSON as per POST_SYSTEM.\"\"\"

    messages = build_messages(POST_SYSTEM, user_prompt)
    try:
        resp = call_llm(provider, api_key, messages, max_tokens=500, temperature=0.6)
        raw = resp.get("text","")
        # try parse JSON
        parsed = None
        try:
            parsed = json.loads(raw)
        except Exception:
            # return raw text if JSON parse fails
            return jsonify({"raw": raw})
        return jsonify(parsed)
    except Exception as e:
        return jsonify({"error":"LLM call failed", "detail": str(e)}), 500

# protected admin route placeholder (batch generation)
@app.route("/api/generate_all", methods=["POST"])
def generate_all():
    token = request.headers.get("X-ADMIN-TOKEN") or request.form.get("admin_pass")
    if token != ADMIN_PASS:
        return jsonify({"error":"unauthorized"}), 403
    return jsonify({"status":"ok", "message":"Batch endpoint placeholder"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("PORT",5000)))
