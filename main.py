from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI
import os

app = Flask(__name__)

# Get API key from environment (Render → Environment → OPENAI_API_KEY)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

ABTROW_PROMPT = """
You are Abtrow AI — a professional, friendly, and knowledgeable Study Abroad Advisor
for students from Myanmar and Asia.

========================
COMMUNICATION STYLE
========================
- Use clear, fluent ENGLISH as the main language.
- If the student writes mostly in Burmese, answer mainly in Burmese and support with key
  English terms (e.g. “conditional offer”, “CAS”, “tuition fee”).
- If the student writes mostly in English, answer mainly in English but you may add
  short Burmese explanation lines for difficult or important points.
- Always sound like a real, trained education consultant: polite, confident, practical.
- Use short paragraphs, bullet points, and numbered steps for clarity.
- Avoid robotic / generic AI phrases.

========================
SCOPE OF ADVICE
========================
Your role:
- Explain university entry requirements, course selection, conditional/unconditional offers,
  CAS, credibility interview basics, tuition fees, and scholarships.
- Compare countries and programs at a high level (UK, Canada, Australia, USA, Europe, etc.).
- Provide general visa process guidance only. YOU ARE NOT AN IMMIGRATION LAWYER.

When something depends on official rules or can change quickly, you MUST say clearly:
“Please double-check this on the official website before making a decision.”

========================
DATA SOURCES – UNIVERSITIES / PROGRAMS / COUNTRIES
========================
When helping the student explore universities, programs, or destination countries, you should:
1) Recommend that they search and shortlist using these platforms:
   - upGrad GSP institution partners: https://upgradgsp.com/institution-partners/
   - ApplyBoard: https://www.applyboard.com/
2) You DO NOT have live access to these websites, so:
   - Do NOT invent specific, detailed program information that you are not sure about.
   - Instead, give general guidance (e.g., “many UK MSc programmes require IELTS 6.0–6.5”),
     and then say something like:
     “For exact, updated details, please check the university page on upGrad GSP or ApplyBoard.”
3) Encourage the student to:
   - Tell you the country, subject area, budget, and any university names they found on those sites.
   - Paste program links or names so you can discuss and explain them.

NEVER claim that a specific university is definitely on upGrad GSP or ApplyBoard unless the
student has already told you that.

========================
VISA / VFS / UKVI INFORMATION
========================
For visa-related questions you MUST:
- Give only general guidance and typical steps.
- Always suggest they confirm on official websites:

  Visa application centres & process information:
  - VFS Global: https://www.vfsglobal.com/en/individuals/index.html

  Detailed UK student visa information:
  - UKVI / gov.uk Student Visa page:
    https://www.gov.uk/student-visa/apply-online

Rules:
- Never give legal advice or guarantee visa outcomes.
- Use phrases such as:
  “Based on typical UKVI guidance…”,
  “However, please check the latest information on the official gov.uk website or VFS Global
   before you apply.”
- If the question is too legal or case-specific, clearly say you cannot give a final answer and
  they must rely on official sources.

========================
LANGUAGE BEHAVIOUR EXAMPLES
========================
If the student writes in Burmese only:
- Answer mainly in Burmese with professional tone, but keep important terms in English too.
  Example:
  “UK MSc majority က IELTS 6.0 လောက်လိုပါတယ်။ သတ်မှတ်ချက်ကတော့ university마다
   မတူနိုင်လို့ official website မှာ ထပ်စစ်ပေးသင့်ပါတယ်။”

If the student writes in English:
- Answer in polished English and you may add 1–2 short Burmese support sentences when helpful.

========================
GENERAL BEHAVIOUR
========================
1. Do NOT repeat the question; start directly with a helpful answer.
2. Ask for missing information (GPA/degree, IELTS/PTE/Duolingo, budget, preferred country, intake).
3. Use realistic, honest guidance — no over-promising.
4. If you are unsure, say you are unsure and point to upGrad GSP, ApplyBoard, VFS Global,
   or gov.uk for confirmation.
5. Always remain polite, encouraging, and professional. You represent Abtrow Education.
"""

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Abtrow AI – Study Abroad Assistant</title>
  <style>
    body { 
        font-family: system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
        max-width: 780px; 
        margin: 20px auto; 
        padding: 0 12px; 
        background: #0A1A3A;  /* Abtrow Navy Blue */
        color: #F5F5F5;
    }

    #header {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        gap: 12px;
        margin-bottom: 12px;
    }

    #header-logo {
        width: 56px;
        height: 56px;
        border-radius: 999px;
        overflow: hidden;
        border: 2px solid #EAC56A;
        flex-shrink: 0;
        background: #0F1E55;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    #header-logo img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    #header-text h1 {
        margin: 0;
        font-size: 20px;
        color: #F2D98B; /* Gold */
        font-weight: 700;
    }

    #header-text p {
        margin: 2px 0 0 0;
        font-size: 12px;
        color: #D1D5DB;
    }

    #topbar { 
        display: flex; 
        justify-content: flex-end; 
        align-items: center; 
        margin: 4px 0 8px 0; 
    }

    #clearBtn { 
        padding: 6px 12px; 
        border-radius: 999px; 
        border: none;
        background: #E63946; 
        color: white; 
        font-size: 12px;
        cursor: pointer;
    }

    #chat { 
        border-radius: 14px; 
        background: #0F1E55; /* Deep Royal Blue */
        padding: 12px; 
        height: 440px; 
        overflow-y: auto; 
        box-shadow: 0 0 12px rgba(242, 217, 139, 0.15);
        margin-bottom: 10px;
    }

    .msg-user { text-align: right; margin: 8px 0; }
    .msg-user span { 
        display: inline-block; 
        background: #EAC56A; /* Gold */ 
        color: #0A1A3A;      /* Navy text */
        padding: 8px 12px; 
        border-radius: 12px 12px 0 12px; 
        max-width: 82%; 
        font-weight: 600;
        white-space: pre-wrap;
    }

    .msg-bot { text-align: left; margin: 8px 0; }
    .msg-bot span { 
        display: inline-block; 
        background: #112869;  /* Slightly brighter navy */
        color: #F5F5F5; 
        padding: 8px 12px; 
        border-radius: 12px 12px 12px 0; 
        max-width: 82%; 
        border-left: 3px solid #EAC56A; /* Gold accent stripe */
        white-space: pre-wrap;
    }

    #quickButtons {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 10px;
    }

    #quickButtons button {
        padding: 8px 14px;
        border-radius: 999px;
        border: none;
        background: linear-gradient(90deg, #EAC56A, #F2D98B);
        color: #0A1A3A; 
        font-weight: 600;
        font-size: 13px;
        cursor: pointer;
    }

    #quickButtons button:active {
        transform: scale(0.95);
    }

    #inputRow { 
        margin-top: 4px; 
        display: flex; 
        gap: 8px; 
    }

    #inputRow input { 
        flex: 1; 
        padding: 12px; 
        border-radius: 999px; 
        border: 1px solid #EAC56A; 
        background: #0F1E55; 
        color: #F5F5F5;
    }

    #inputRow input::placeholder {
        color: #D1D5DB;
    }

    #inputRow button { 
        padding: 12px 18px; 
        border-radius: 999px; 
        border: none;
        background: linear-gradient(90deg, #EAC56A, #F2D98B);
        color: #0A1A3A; 
        font-weight: 700; 
        cursor: pointer;
    }

    #inputRow button:active { 
        transform: scale(0.97); 
    }
  </style>
</head>
<body>
  <div id="header">
    <div id="header-logo">
      <!-- TODO: Replace the src URL below with your real logo URL -->
      <img src="https://YOUR-LOGO-URL-HERE.png" alt="Abtrow Logo" />
    </div>
    <div id="header-text">
      <h1>Abtrow AI – Study Abroad Assistant</h1>
      <p>Smart guidance for Myanmar and Asian students</p>
    </div>
  </div>

  <div id="topbar">
    <button id="clearBtn" onclick="clearChat()">Clear</button>
  </div>

  <div id="chat"></div>

  <div id="quickButtons">
    <button onclick="quickSend('UK')">UK</button>
    <button onclick="quickSend('New Zealand')">New Zealand</button>
    <button onclick="quickSend('Vietnam')">Vietnam</button>
    <button onclick="quickSend('Singapore')">Singapore</button>
    <button onclick="quickSend('Canada')">Canada</button>
    <button onclick="quickSend('Visa Help')">Visa Help</button>
  </div>

  <div id="inputRow">
    <input id="msg" type="text" placeholder="Ask about courses, visas, scholarships..." />
    <button onclick="sendMsg()">Send</button>
  </div>

  <script>
    const chat = document.getElementById('chat');
    const input = document.getElementById('msg');

    // ✅ Abtrow AI Welcome Message (auto displayed on page load)
    const welcomeMessage = `
🌟 မင်္ဂလာပါ!

နိုင်ငံခြားမှာ ပညာသင်ဖို့ စိတ်ဝင်စားနေသူများအတွက်  
Abtrow Education က မေးမြန်းရာအသေးစိတ် အချက်အလက်အားလုံးကို  
အမြန်ဆုံးနှင့် တိကျမှန်ကန်အဖြေပေးဖို့ အဆင်သင့်ဖြစ်နေပါတယ်။ 🌍✈️  

အသေးစိတ်အချက်အလက်များ၊ တက္ကသိုလ်ရွေးချယ်မှုများ၊  
နိုင်ငံရွေးချယ်မှုများအတွက်  
အောက်ပါ Form ကို နှိပ်ပြီး ဖြည့်ပေးပါ👇  

👉 Application Form:  
https://forms.gle/iW3gj2SENKdB5Ckt9  

မေးမြန်းလိုပါက ဖုန်း သို့မဟုတ် အီးမေးလ်မှတဆင့် ဆက်သွယ်နိုင်ပါတယ်👇  
📞 +၉၅၉ ၈၉၁ ၁၁၈ ၈၇  
📧 info@abtrow.com  

သင့်အိပ်မက်တွေကို အကောင်အထည်ဖော်နိုင်ဖို့  
Abtrow က အမြဲတမ်း အတူရှိနေပါမယ်။ 🚀🎓✨  

🤖 Abtrow AI Chatbot is here to help you with further information.
မေးချင်တာလေးတွေကို အခုချိန်မှာပဲ မေးမြန်းနိုင်ပါတယ်။
`;

    function showWelcome() {
        addMessage(welcomeMessage, 'bot');
    }

    function addMessage(text, sender) {
      const div = document.createElement('div');
      div.className = sender === 'user' ? 'msg-user' : 'msg-bot';
      const span = document.createElement('span');
      span.textContent = text;
      div.appendChild(span);
      chat.appendChild(div);
      chat.scrollTop = chat.scrollHeight;
    }

    async function sendMsg() {
      const text = input.value.trim();
      if (!text) return;
      addMessage(text, 'user');
      input.value = '';

      try {
        const res = await fetch('/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text })
        });
        const data = await res.json();
        addMessage(data.reply, 'bot');
      } catch (e) {
        addMessage('Sorry, there was an error connecting to Abtrow AI.', 'bot');
      }
    }

    function clearChat() {
      chat.innerHTML = '';
      showWelcome();
    }

    function quickSend(text) {
      addMessage(text, 'user');
      sendQuick(text);
    }

    async function sendQuick(text) {
      try {
        const res = await fetch('/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text })
        });
        const data = await res.json();
        addMessage(data.reply, 'bot');
      } catch (e) {
        addMessage('Sorry, there was an error connecting to Abtrow AI.', 'bot');
      }
    }

    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') sendMsg();
    });

    // Show the welcome message automatically on first load
    window.onload = showWelcome;
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

@app.route("/chat", methods=["POST"])
def chat_endpoint():
    data = request.get_json() or {}
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "Please type a question first."})

    try:
        completion = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": ABTROW_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )
        reply = completion.choices[0].message.content
        return jsonify({"reply": reply})
    except Exception as e:
        print("ERROR:", e)
        return jsonify({"reply": "Sorry, the AI had an error: " + str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

