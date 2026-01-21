from flask import Flask, request, jsonify, render_template_string
import threading
import asyncio
import os
import socket
import bot

app = Flask(__name__)

@app.route('/join', methods=['GET', 'POST'])
def join_team():
    if not bot.loop:
        return jsonify({"error": "bot not running"}), 400

    if request.method == 'GET':
        team_code = request.args.get('tc')
        emote_id = request.args.get('ei')
        uids = [request.args.get(f'uid{i}') for i in range(1, 7) if request.args.get(f'uid{i}')]

    else:  # POST
        data = request.get_json(silent=True) or {}
        team_code = data.get('tc')
        emote_id = data.get('ei')
        uids = data.get('uids', [])

    if not team_code or not emote_id or not uids:
        return jsonify({"error": "missing params"}), 400

    asyncio.run_coroutine_threadsafe(
        bot.perform_emote(team_code, uids, int(emote_id)),
        bot.loop
    )

    return jsonify({"status": "success"})
    
@app.route("/")
def home():
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Emote Join</title>

<style>
*{
    box-sizing:border-box;
    -webkit-tap-highlight-color: transparent; /* 🚫 remove blue tap */
}

body{
    margin:0;
    background:#fff8fb;
    font-family:-apple-system,BlinkMacSystemFont,sans-serif;
    color:#6b2d40;
}
.container{
    max-width:420px;
    margin:auto;
    padding:20px;
}
h1{
    text-align:center;
    color:#b84a6a;
    margin-bottom:20px;
}
.card{
    background:#ffffff;
    border-radius:20px;
    padding:16px;
    margin-bottom:15px;
    box-shadow:0 6px 20px rgba(255,210,225,0.22);
}
label{
    font-weight:600;
    display:block;
    margin-bottom:6px;
}
input{
    width:100%;
    padding:12px;
    border-radius:14px;
    border:1px solid #f6d3df;
    font-size:15px;
    background:#fff;
    margin-bottom:10px;
}

/* 🔒 Remove focus/active blue */
button{
    border:none;
    cursor:pointer;
    font-family:inherit;
    outline:none;
}
button:focus,
button:active{
    outline:none;
    box-shadow:none;
    background-clip:padding-box;
}

/* UID buttons */
.add, .remove{
    flex:1;
    padding:12px;
    border-radius:999px;
    font-weight:bold;
    background:#ffe6ee;
    color:#8b3051;
}
.single{
    width:100%;
    padding:12px;
    border-radius:999px;
    background:#ffe6ee;
    color:#8b3051;
    font-weight:bold;
}
.btn-row{
    display:flex;
    gap:10px;
}

/* Primary buttons */
.primary-pill{
    width:100%;
    margin-top:10px;
    padding:14px;
    border-radius:999px;
    background:linear-gradient(135deg,#ffd6e7,#ffb6cf);
    color:#8b3051;
    font-size:16px;
    font-weight:bold;
}

/* Instagram button (same style, no blue tap) */
.insta-pill{
    width:100%;
    margin-top:22px;
    padding:16px;
    border-radius:999px;
    background:linear-gradient(135deg,#ffd6e7,#ffb6cf);
    color:#8b3051;
    font-size:15px;
    font-weight:bold;
}

/* Success popup */
.popup-bg{
    position:fixed;
    inset:0;
    display:none;
    align-items:center;
    justify-content:center;
    z-index:999;
}
.popup-pill{
    padding:16px 32px;
    border-radius:999px;
    font-size:18px;
    font-weight:700;
    background:linear-gradient(135deg,#ffe6f0,#ffd1e6);
    color:#a83e63;
    box-shadow:0 12px 30px rgba(255,180,210,0.45);
}
</style>
</head>

<body>
<div class="container">

<h1>🌸 Niva Emote</h1>

<div class="card">
    <label>🎟 Team Code</label>
    <input id="tc" placeholder="Enter team code">
</div>

<div class="card">
    <label>👥 Player UIDs</label>
    <div id="uids">
        <input placeholder="UID 1">
    </div>
    <div id="uidButtons"></div>
</div>

<div class="card">
    <label>🎭 Emote ID</label>
    <input id="ei" placeholder="Enter emote id">
</div>

<button class="primary-pill" onclick="submitForm()">✨ Start Emote</button>

<button class="insta-pill"
onclick="window.open('https://instagram.com/ft_rosie._','_blank')">
💛 Let’s be friends on Instagram<br>@ft_rosie._
</button>

</div>

<div class="popup-bg" id="popup">
    <div class="popup-pill">Success🫶🏻</div>
</div>

<script>
let uidCount = 1;
const maxUID = 6;

function renderButtons(){
    const box=document.getElementById("uidButtons");
    box.innerHTML="";
    if(uidCount===1){
        box.innerHTML=`<button class="single" onclick="addUID()">➕ Add UID</button>`;
    }else if(uidCount<maxUID){
        box.innerHTML=`
        <div class="btn-row">
            <button class="add" onclick="addUID()">➕ Add UID</button>
            <button class="remove" onclick="removeUID()">➖ Remove UID</button>
        </div>`;
    }else{
        box.innerHTML=`<button class="single" onclick="removeUID()">➖ Remove UID</button>`;
    }
}
function addUID(){
    if(uidCount>=maxUID) return;
    uidCount++;
    const i=document.createElement("input");
    i.placeholder="UID "+uidCount;
    document.getElementById("uids").appendChild(i);
    renderButtons();
}
function removeUID(){
    if(uidCount<=1) return;
    document.getElementById("uids").lastElementChild.remove();
    uidCount--;
    renderButtons();
}
renderButtons();

function showPopup(){
    const p=document.getElementById("popup");
    p.style.display="flex";
    setTimeout(()=>{p.style.display="none";},500);
}
async function submitForm(){
    const tc=document.getElementById("tc").value;
    const ei=document.getElementById("ei").value;
    const uids=[];
    document.querySelectorAll("#uids input").forEach(i=>{
        if(i.value.trim()) uids.push(i.value.trim());
    });
    const res=await fetch("/join",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({tc,ei,uids})
    });
    const data=await res.json();
    if(data.status==="success") showPopup();
}
</script>

</body>
</html>
""")

def find_free_port(start=8080, end=65535):
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('0.0.0.0', port)) != 0:
                return port
    raise RuntimeError("No free port available")

if __name__ == "__main__":
    # 🔥 Auto-start bot
    t = threading.Thread(target=bot.start_bot, daemon=True)
    t.start()

    # 🚀 Start Flask server

    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
