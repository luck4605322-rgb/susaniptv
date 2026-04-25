import streamlit as st
import time
import pandas as pd

# ==================== 1. 多语言字典（v1.8.1 完整版，已修复所有语法问题） ====================
LANGUAGES = {
    "简体中文": {
        "title": "IPTVNator 网页批量检测工具 v1.8.1（客户端检测）--作者susan, WhatsApp: +8615573857383",
        "username": "用户名", 
        "password": "密码", 
        "servers": "服务器地址（一行一个）",
        "start_btn": "🚀 从我的本地网络开始批量检测", 
        "result_label": "检测结果", 
        "warning": "请填写完整信息！",
        "testing": "正在从您的浏览器直接检测...",
        "header_server": "服务器", 
        "header_status": "状态", 
        "header_info": "详细信息",
        "your_ip": "您的公网 IP", 
        "client_note": "✅ 检测现在从您的本地网络发起（真实家宽/流量/VPN）"
    },
    "English": {
        "title": "IPTVNator Web Batch Tester v1.8.1 (Client-Side) --Author susan, WhatsApp: +8615573857383",
        "username": "Username", 
        "password": "Password", 
        "servers": "Server Addresses (one per line)",
        "start_btn": "🚀 Start Batch Test from My Local Network", 
        "result_label": "Test Results", 
        "warning": "Please fill in all fields!",
        "testing": "Testing directly from your browser...",
        "header_server": "Server", 
        "header_status": "Status", 
        "header_info": "Details",
        "your_ip": "Your Public IP", 
        "client_note": "✅ Detection now runs from your local network (real home broadband / mobile / VPN)"
    },
    "Español": {
        "title": "Probador Masivo IPTV v1.8.1 (Detección del Cliente) --Autor susan, WhatsApp: +8615573857383",
        "username": "Usuario", 
        "password": "Contraseña", 
        "servers": "Direcciones del servidor (una por línea)",
        "start_btn": "🚀 Iniciar prueba masiva desde mi red local", 
        "result_label": "Resultados de la prueba", 
        "warning": "¡Por favor complete toda la información!",
        "testing": "Probando directamente desde su navegador...",
        "header_server": "Servidor", 
        "header_status": "Estado", 
        "header_info": "Detalles",
        "your_ip": "Su IP Pública", 
        "client_note": "✅ La detección ahora se ejecuta desde su red local (fibra / móvil / VPN real)"
    },
    "Français": {
        "title": "Testeur IPTV Batch v1.8.1 (Côté Client) --Auteur susan, WhatsApp: +8615573857383",
        "username": "Nom d'utilisateur", 
        "password": "Mot de passe", 
        "servers": "Adresses des serveurs (une par ligne)",
        "start_btn": "🚀 Lancer le test depuis mon réseau local", 
        "result_label": "Résultats du test", 
        "warning": "Veuillez remplir toutes les informations !",
        "testing": "Test en cours directement depuis votre navigateur...",
        "header_server": "Serveur", 
        "header_status": "Statut", 
        "header_info": "Détails",
        "your_ip": "Votre IP Publique", 
        "client_note": "✅ Le test s'exécute maintenant depuis votre réseau local (fibre / mobile / VPN réel)"
    },
    "Deutsch": {
        "title": "IPTV Batch Tester v1.8.1 (Client-Seite) --Autor susan, WhatsApp: +8615573857383",
        "username": "Benutzername", 
        "password": "Passwort", 
        "servers": "Serveradressen (eine pro Zeile)",
        "start_btn": "🚀 Batch-Test von meinem lokalen Netzwerk starten", 
        "result_label": "Testergebnisse", 
        "warning": "Bitte füllen Sie alle Felder aus!",
        "testing": "Testet direkt von Ihrem Browser aus...",
        "header_server": "Server", 
        "header_status": "Status", 
        "header_info": "Details",
        "your_ip": "Ihre öffentliche IP", 
        "client_note": "✅ Die Prüfung läuft jetzt von Ihrem lokalen Netzwerk (echtes Breitband / Mobil / VPN)"
    },
    "Português": {
        "title": "Testador IPTV em Lote v1.8.1 (Lado do Cliente) --Autor susan, WhatsApp: +8615573857383",
        "username": "Nome de usuário", 
        "password": "Senha", 
        "servers": "Endereços dos servidores (um por linha)",
        "start_btn": "🚀 Iniciar teste em lote da minha rede local", 
        "result_label": "Resultados do teste", 
        "warning": "Por favor, preencha todas as informações!",
        "testing": "Testando diretamente do seu navegador...",
        "header_server": "Servidor", 
        "header_status": "Status", 
        "header_info": "Detalhes",
        "your_ip": "Seu IP Público", 
        "client_note": "✅ A detecção agora é feita da sua rede local (fibra / móvel / VPN real)"
    },
    "Italiano": {
        "title": "Tester IPTV Batch v1.8.1 (Lato Client) --Autore susan, WhatsApp: +8615573857383",
        "username": "Nome utente", 
        "password": "Password", 
        "servers": "Indirizzi server (uno per riga)",
        "start_btn": "🚀 Avvia test batch dalla mia rete locale", 
        "result_label": "Risultati del test", 
        "warning": "Si prega di compilare tutte le informazioni!",
        "testing": "Test in corso direttamente dal tuo browser...",
        "header_server": "Server", 
        "header_status": "Stato", 
        "header_info": "Dettagli",
        "your_ip": "Il tuo IP Pubblico", 
        "client_note": "✅ Il test ora viene eseguito dalla tua rete locale (fibra / mobile / VPN reale)"
    }
}

# ==================== 2. Streamlit 配置 ====================
st.set_page_config(page_title="IPTVNator Client Tester v1.8.1", layout="wide", page_icon="📺")

lang_choice = st.sidebar.selectbox("🌐 Language / 语言 / Idioma", list(LANGUAGES.keys()))
t = LANGUAGES[lang_choice]

st.title(t["title"])
st.markdown("---")

# 显示当前访问者 IP
@st.cache_data(ttl=3600)
def get_public_ip():
    try:
        import requests
        return requests.get("https://ifconfig.me/ip", timeout=5).text.strip()
    except:
        return "Unknown / 无法获取"

current_ip = get_public_ip()

st.sidebar.subheader(t["your_ip"])
st.sidebar.code(current_ip, language="bash")
st.sidebar.caption(t.get("client_note", "检测从客户端浏览器发起"))

# ==================== 3. 输入区域 ====================
col_input, col_info = st.columns([2, 1])

with col_input:
    c1, c2 = st.columns(2)
    with c1:
        username = st.text_input(t["username"])
    with c2:
        password = st.text_input(t["password"], type="password")
    
    servers_text = st.text_area(t["servers"], height=250,
                                placeholder="http://example.com:8080\nhttps://iptv.example.com")

with col_info:
    st.info(f"""
    **💡 Important Tips / 重要提示:**
    - 检测将**从您的浏览器直接发起**，使用您本地的真实网络
    - 支持 HTTP/HTTPS，自动添加 http:// 前缀
    - 推荐一次不要超过 50 个服务器
    - WhatsApp: **+8615573857383**
    """)

# ==================== 4. 核心：JavaScript 客户端检测 ====================
if st.button(t["start_btn"], type="primary", use_container_width=True):
    if not username or not password or not servers_text.strip():
        st.error(t["warning"])
    else:
        servers = [s.strip() for s in servers_text.splitlines() if s.strip()]
        
        if not servers:
            st.error("没有有效的服务器地址！" if lang_choice == "简体中文" else "No valid server addresses!")
            st.stop()

        # 安全的 JS 代码（对引号进行转义）
        safe_username = username.replace('"', '\\"').replace("'", "\\'")
        safe_password = password.replace('"', '\\"').replace("'", "\\'")

        js_code = f"""
        <script>
        async function testIPTV() {{
            const username = "{safe_username}";
            const password = "{safe_password}";
            const servers = {servers};
            
            const results = [];
            const progressContainer = document.createElement('div');
            progressContainer.innerHTML = `
                <h3>{t.get("testing", "Testing from your browser...")}</h3>
                <div style="width:100%; background:#333; height:25px; border-radius:12px; overflow:hidden; margin:15px 0;">
                    <div id="bar" style="width:0%; height:100%; background:linear-gradient(90deg, #00ff88, #00cc66); transition:width 0.4s ease;"></div>
                </div>
                <p id="status" style="font-family:monospace; text-align:center;"></p>
            `;
            document.body.appendChild(progressContainer);

            const bar = document.getElementById('bar');
            const statusEl = document.getElementById('status');

            for (let i = 0; i < servers.length; i++) {{
                let server = servers[i];
                if (!server.startsWith('http')) server = 'http://' + server;
                server = server.replace(/\\/$/, '');

                const baseUrl = `${{server}}/player_api.php?username=${{encodeURIComponent(username)}}&password=${{encodeURIComponent(password)}}`;
                const startTime = Date.now();

                try {{
                    const controller = new AbortController();
                    const timeoutId = setTimeout(() => controller.abort(), 12000);

                    const resp = await fetch(baseUrl, {{
                        method: 'GET',
                        headers: {{ 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' }},
                        signal: controller.signal
                    }});

                    clearTimeout(timeoutId);
                    const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);

                    let statusText = '❌ Fail';
                    let detail = '';

                    if (resp.ok) {{
                        try {{
                            const data = await resp.json();
                            if (data.user_info) {{
                                const ui = data.user_info;
                                const exp = ui.exp_date;
                                const expDate = exp && !isNaN(parseInt(exp)) 
                                    ? new Date(parseInt(exp) * 1000).toISOString().split('T')[0] 
                                    : 'Never';
                                detail = `Status: ${{ui.status || 'Active'}} | Exp: ${{expDate}} | ${{elapsed}}s`;
                                statusText = '✅ Active';
                            }} else {{
                                detail = `Login Failed | ${{elapsed}}s`;
                            }}
                        }} catch(e) {{
                            detail = `Invalid JSON | ${{elapsed}}s`;
                        }}
                    }} else {{
                        detail = `HTTP ${{resp.status}} | ${{elapsed}}s`;
                    }}
                    results.push({{Server: server, Status: statusText, Details: detail}});
                }} catch (err) {{
                    const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
                    let msg = err.name === 'AbortError' ? 'Timeout' : 'Error/Unreachable';
                    results.push({{Server: server, Status: '❌ Error', Details: `${{msg}} | ${{elapsed}}s`}});
                }}

                const percent = Math.round(((i + 1) / servers.length) * 100);
                bar.style.width = percent + '%';
                statusEl.textContent = `Testing: ${{i+1}}/${{servers.length}}  (${{percent}}%)`;
            }}

            let html = `
                <h3 style="margin-top:30px;">${t["result_label"]}</h3>
                <table style="width:100%; border-collapse:collapse; margin-top:15px; font-size:14px;">
                    <thead>
                        <tr style="background:#1e1e1e;">
                            <th style="padding:12px; border:1px solid #444; text-align:left;">${t["header_server"]}</th>
                            <th style="padding:12px; border:1px solid #444; text-align:left;">${t["header_status"]}</th>
                            <th style="padding:12px; border:1px solid #444; text-align:left;">${t["header_info"]}</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            results.forEach(r => {{
                const color = r.Status.includes('✅') ? '#00ff00' : '#ff4444';
                html += `
                    <tr>
                        <td style="padding:10px; border:1px solid #444;">${r.Server}</td>
                        <td style="padding:10px; border:1px solid #444; color:${color}; font-weight:bold;">${r.Status}</td>
                        <td style="padding:10px; border:1px solid #444; font-family:monospace;">${r.Details}</td>
                    </tr>
                `;
            }});

            html += `</tbody></table><br><p style="color:#888; text-align:center;">WhatsApp: +8615573857383</p>`;

            const resultDiv = document.createElement('div');
            resultDiv.innerHTML = html;
            document.body.appendChild(resultDiv);
            window.scrollTo(0, document.body.scrollHeight);
        }}

        testIPTV();
        </script>
        """

        st.components.v1.html(js_code, height=900, scrolling=True)
        st.success("✅ 客户端检测已启动！结果将直接显示在下方（由您的浏览器执行）。 WhatsApp: +8615573857383")
