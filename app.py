import streamlit as st
import json

# ==================== 多国语言字典 ====================
LANGUAGES = {
    "简体中文": {
        "title": "IPTVNator 批量检测工具 v1.8",
        "username": "用户名:",
        "password": "密码:",
        "servers": "服务器地址（一行一个）:",
        "example": "填入示例",
        "start_btn": "🚀 开始批量检测",
        "lang_label": "界面语言 / Language:",
        "footer": "v1.8 • 纯浏览器端检测 • 独立进度界面",
        "warning": "请填写服务器列表、账号和密码！",
        "cors_warning": "⚠️ 注意：很多 IPTV 服务器不支持 CORS，可能会显示“连接失败”。这是浏览器安全限制，无法避免。",
    },
    "English": {
        "title": "IPTVNator Batch Tester v1.8",
        "username": "Username:",
        "password": "Password:",
        "servers": "Server Addresses (one per line):",
        "example": "Load Example",
        "start_btn": "🚀 Start Batch Test",
        "lang_label": "Interface Language:",
        "footer": "v1.8 • Pure Browser Detection • Standalone Progress Panel",
        "warning": "Please fill in servers, username and password!",
        "cors_warning": "⚠️ Note: Many IPTV servers do not support CORS. 'Connection failed' is normal due to browser restrictions.",
    },
    "Español": {
        "title": "IPTVNator Prueba por Lotes v1.8",
        "username": "Usuario:",
        "password": "Contraseña:",
        "servers": "Direcciones del servidor (una por línea):",
        "example": "Cargar ejemplo",
        "start_btn": "🚀 Iniciar prueba por lotes",
        "lang_label": "Idioma de la interfaz:",
        "footer": "v1.8 • Detección en navegador",
        "warning": "¡Complete servidores, usuario y contraseña!",
        "cors_warning": "⚠️ Muchos servidores IPTV no soportan CORS.",
    },
    "Français": {
        "title": "Outil de Test IPTVNator v1.8",
        "username": "Nom d'utilisateur:",
        "password": "Mot de passe:",
        "servers": "Adresses du serveur (une par ligne):",
        "example": "Charger exemple",
        "start_btn": "🚀 Lancer le test par lots",
        "lang_label": "Langue de l'interface:",
        "footer": "v1.8 • Détection côté navigateur",
        "warning": "Veuillez remplir serveurs, nom d'utilisateur et mot de passe !",
        "cors_warning": "⚠️ De nombreux serveurs IPTV ne supportent pas CORS.",
    }
}

st.set_page_config(page_title="IPTVNator 批量检测工具", layout="wide", page_icon="🚀")

lang = st.selectbox(LANGUAGES["简体中文"]["lang_label"], options=list(LANGUAGES.keys()), index=0)
trans = LANGUAGES[lang]

st.title("🚀 " + trans["title"])

col1, col2 = st.columns([2, 1])
with col1:
    username = st.text_input(trans["username"], placeholder="username")
    password = st.text_input(trans["password"], type="password", placeholder="password")
with col2:
    if st.button(trans["example"], use_container_width=True):
        st.session_state["servers"] = "http://example.com:8080\nhttp://test.tv:12345"

servers_input = st.text_area(
    trans["servers"],
    height=160,
    value=st.session_state.get("servers", ""),
    placeholder="http://server.com:8080\nhttp://backup.tv:1234"
)

st.warning(trans["cors_warning"])

if st.button(trans["start_btn"], type="primary", use_container_width=True):
    servers = [s.strip() for s in servers_input.strip().splitlines() if s.strip()]
    username_str = username.strip()
    password_str = password.strip()

    if not servers or not username_str or not password_str:
        st.error(trans["warning"])
        st.stop()

    # 转义处理
    username_escaped = username_str.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'")
    password_escaped = password_str.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'")

    # ==================== 完整独立检测页面 (推荐方式) ====================
    detection_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: system-ui, sans-serif; padding: 20px; background: #f4f6f9; }}
            .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
            .progress-container {{ height: 30px; background: #e9ecef; border-radius: 8px; overflow: hidden; margin: 20px 0; }}
            .progress-bar {{ height: 100%; background: linear-gradient(90deg, #28a745, #20c997); width: 0%; transition: width 0.5s ease; }}
            .log {{ background: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; height: 480px; overflow-y: auto; font-family: monospace; white-space: pre-wrap; font-size: 14px; line-height: 1.6; border-radius: 8px; }}
            .header {{ color: #28a745; margin-bottom: 15px; }}
        </style>
    </head>
    <body>
    <div class="container">
        <h2 class="header">🚀 {trans.get("running", "正在检测").replace("{0}", str(len(servers)))}</h2>
        
        <div class="progress-container">
            <div id="progressBar" class="progress-bar"></div>
        </div>
        <div id="progressText" style="text-align:center; font-weight:bold; margin-bottom:15px;">0/{len(servers)} (0%)</div>
        
        <div id="log" class="log"></div>
    </div>

    <script>
    const username = "{username_escaped}";
    const password = "{password_escaped}";
    const servers = {json.dumps(servers)};
    const trans = {json.dumps(trans)};

    let completed = 0;

    async function testServer(server, index) {{
        if (!server.startsWith("http")) server = "http://" + server;
        server = server.replace(/\/$/, "");
        const baseUrl = server + "/player_api.php?username=" + encodeURIComponent(username) + "&password=" + encodeURIComponent(password);

        const startTime = Date.now();
        document.getElementById("log").innerHTML += `[${{index}}/${{servers.length}}] 检测中 → ${{server}}\\n`;
        document.getElementById("log").scrollTop = document.getElementById("log").scrollHeight;

        try {{
            const controller = new AbortController();
            const timeout = setTimeout(() => controller.abort(), 15000);

            const resp = await fetch(baseUrl, {{
                method: "GET",
                headers: {{ "Accept": "application/json" }},
                signal: controller.signal,
                mode: "cors"
            }});

            clearTimeout(timeout);
            const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);

            if (resp.status !== 200) {{
                document.getElementById("log").innerHTML += `→ ❌ HTTP错误 ${{resp.status}} | 耗时 ${{elapsed}}s\\n\\n`;
            }} else {{
                const data = await resp.json();
                if (!data || !data.user_info) {{
                    document.getElementById("log").innerHTML += `→ ❌ 登录失败 (无 user_info) | 耗时 ${{elapsed}}s\\n\\n`;
                }} else {{
                    const ui = data.user_info;
                    let exp = ui.exp_date || "永久";
                    if (/^\\d+$/.test(String(exp))) {{
                        exp = new Date(parseInt(exp) * 1000).toLocaleString();
                    }}
                    const msg = `✅ 可用 | 耗时 ${{elapsed}}s | 状态: ${{ui.status || "Unknown"}} | 过期: ${{exp}}`;
                    document.getElementById("log").innerHTML += `→ ${{msg}}\\n\\n`;
                }}
            }}
        }} catch (err) {{
            let msg = "❌ 未知错误";
            if (err.name === "AbortError") msg = "❌ 超时 (>15秒)";
            else if ((err.message || "").toLowerCase().includes("cors") || (err.message || "").includes("fetch")) {{
                msg = "❌ 连接失败 (不可达或被阻挡)";
            }}
            document.getElementById("log").innerHTML += `→ ${{msg}}\\n\\n`;
        }}

        document.getElementById("log").scrollTop = document.getElementById("log").scrollHeight;
        completed++;

        const percent = Math.round((completed / servers.length) * 100);
        document.getElementById("progressBar").style.width = percent + "%";
        document.getElementById("progressText").textContent = `${{completed}}/${{servers.length}} (${{percent}}%)`;
    }}

    // 开始检测
    (async () => {{
        for (let i = 0; i < servers.length; i++) {{
            await testServer(servers[i], i + 1);
            await new Promise(r => setTimeout(r, 400));
        }}
        document.getElementById("log").innerHTML += `\\n✅ 批量检测完成！共检测 ${{servers.length}} 个服务器。\\n`;
        document.getElementById("log").scrollTop = document.getElementById("log").scrollHeight;
    }})();
    </script>
    </body>
    </html>
    """

    st.components.v1.html(detection_html, height=720, scrolling=True)

st.caption(trans["footer"])
st.info("💡 检测完全在您的浏览器中运行 • 结果更真实 • CORS 失败属于正常现象")
