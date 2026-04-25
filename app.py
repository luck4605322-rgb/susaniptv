import streamlit as st
import json

# ==================== 多国语言字典 ====================
LANGUAGES = {
    "简体中文": {
        "title": "IPTVNator 批量检测工具 v1.6 - 浏览器端检测",
        "username": "用户名:",
        "password": "密码:",
        "servers": "服务器地址（一行一个）:",
        "example": "填入示例",
        "start_btn": "🚀 开始批量检测",
        "lang_label": "界面语言 / Language:",
        "footer": "v1.6 • 纯浏览器端检测 • 实时进度条",
        "warning": "请填写服务器列表、账号和密码！",
        "running": "🚀 正在检测 {0} 个服务器...",
        "detecting": "[{0}/{1}] 检测中 → {2}",
        "complete": "✅ 检测完成！共检测 {0} 个服务器。",
        "http_error": "❌ HTTP错误 {0} | 耗时 {1}s",
        "no_userinfo": "❌ 登录失败（无 user_info） | 耗时 {0}s",
        "timeout": "❌ 超时 (>15秒)",
        "conn_fail": "❌ 连接失败（不可达或被阻挡）",
        "unknown": "❌ 未知错误",
        "available": "✅ 可用 | 耗时 {0}s | 状态: {1} | 过期: {2}",
        "cors_warning": "⚠️ 注意：很多 IPTV 服务器不支持 CORS，可能会显示连接失败。这是浏览器安全限制。",
        "progress_text": "检测进度：{0}/{1} ({2}%)"
    },
    "English": {
        "title": "IPTVNator Batch Tester v1.6 - Client-side Detection",
        "username": "Username:",
        "password": "Password:",
        "servers": "Server Addresses (one per line):",
        "example": "Load Example",
        "start_btn": "🚀 Start Batch Test",
        "lang_label": "Interface Language:",
        "footer": "v1.6 • Pure Browser-side Test • Real-time Progress",
        "warning": "Please fill in servers, username and password!",
        "running": "🚀 Testing {0} servers...",
        "detecting": "[{0}/{1}] Testing → {2}",
        "complete": "✅ Test completed! Tested {0} servers.",
        "http_error": "❌ HTTP Error {0} | Time {1}s",
        "no_userinfo": "❌ Login failed (no user_info) | Time {0}s",
        "timeout": "❌ Timeout (>15s)",
        "conn_fail": "❌ Connection failed (unreachable or blocked)",
        "unknown": "❌ Unknown error",
        "available": "✅ Available | Time {0}s | Status: {1} | Exp: {2}",
        "cors_warning": "⚠️ Note: Many IPTV servers do not support CORS. Connection failed is common due to browser restrictions.",
        "progress_text": "Progress: {0}/{1} ({2}%)"
    },
    "Español": {
        "title": "Herramienta de Prueba IPTVNator v1.6",
        "username": "Usuario:",
        "password": "Contraseña:",
        "servers": "Direcciones del servidor (una por línea):",
        "example": "Cargar ejemplo",
        "start_btn": "🚀 Iniciar prueba por lotes",
        "lang_label": "Idioma de la interfaz:",
        "footer": "v1.6 • Detección del lado del cliente",
        "warning": "¡Por favor complete servidores, usuario y contraseña!",
        "running": "🚀 Probando {0} servidores...",
        "detecting": "[{0}/{1}] Probando → {2}",
        "complete": "✅ ¡Prueba completada! Se probaron {0} servidores.",
        "http_error": "❌ Error HTTP {0} | Tiempo {1}s",
        "no_userinfo": "❌ Fallo de inicio de sesión (sin user_info) | Tiempo {0}s",
        "timeout": "❌ Tiempo de espera (>15s)",
        "conn_fail": "❌ Fallo de conexión",
        "unknown": "❌ Error desconocido",
        "available": "✅ Disponible | Tiempo {0}s | Estado: {1} | Expira: {2}",
        "cors_warning": "⚠️ Muchos servidores IPTV no soportan CORS.",
        "progress_text": "Progreso: {0}/{1} ({2}%)"
    },
    "Français": {
        "title": "Outil de Test IPTVNator v1.6",
        "username": "Nom d'utilisateur:",
        "password": "Mot de passe:",
        "servers": "Adresses du serveur (une par ligne):",
        "example": "Charger exemple",
        "start_btn": "🚀 Lancer le test par lots",
        "lang_label": "Langue de l'interface:",
        "footer": "v1.6 • Détection côté client",
        "warning": "Veuillez remplir les serveurs, nom d'utilisateur et mot de passe !",
        "running": "🚀 Test de {0} serveurs...",
        "detecting": "[{0}/{1}] Test en cours → {2}",
        "complete": "✅ Test terminé ! {0} serveurs testés.",
        "http_error": "❌ Erreur HTTP {0} | Temps {1}s",
        "no_userinfo": "❌ Échec de connexion (pas de user_info) | Temps {0}s",
        "timeout": "❌ Délai dépassé (>15s)",
        "conn_fail": "❌ Échec de connexion",
        "unknown": "❌ Erreur inconnue",
        "available": "✅ Disponible | Temps {0}s | Statut: {1} | Expiration: {2}",
        "cors_warning": "⚠️ De nombreux serveurs IPTV ne supportent pas CORS.",
        "progress_text": "Progression: {0}/{1} ({2}%)"
    }
}

# ==================== 主界面 ====================
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
    height=180, 
    value=st.session_state.get("servers", ""),
    placeholder="一行一个服务器地址\nhttp://your-server.com:8080"
)

st.warning(trans["cors_warning"])

if st.button(trans["start_btn"], type="primary", use_container_width=True):
    servers = [s.strip() for s in servers_input.strip().splitlines() if s.strip()]
    username_str = username.strip()
    password_str = password.strip()

    if not servers or not username_str or not password_str:
        st.error(trans["warning"])
        st.stop()

    # ==================== 纯前端 JavaScript 检测（已修复 f-string 问题） ====================
    js_code = """
    <script>
    const username = "{username_str}";
    const password = "{password_str}";
    const servers = {servers_json};
    const trans = {trans_json};

    // 创建检测界面
    let html = `
        <div style="margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 10px; background: #f8f9fa;">
            <h3>${trans.running.replace('{0}', servers.length)}</h3>
            
            <div style="margin: 15px 0;">
                <div id="progressContainer" style="height: 28px; background: #e0e0e0; border-radius: 6px; overflow: hidden;">
                    <div id="progressBar" style="height: 100%; background: linear-gradient(90deg, #4CAF50, #45a049); width: 0%; transition: width 0.4s ease;"></div>
                </div>
                <div id="progressText" style="text-align: center; margin-top: 8px; font-weight: bold; color: #333;">
                    0/${servers.length} (0%)
                </div>
            </div>
            
            <div id="log" style="background: #ffffff; border: 1px solid #ccc; padding: 15px; height: 420px; overflow-y: auto; 
                                 font-family: monospace; white-space: pre-wrap; font-size: 14px; line-height: 1.5;"></div>
        </div>
    `;

    const container = document.createElement("div");
    container.innerHTML = html;
    document.body.appendChild(container);

    const progressBar = document.getElementById("progressBar");
    const progressText = document.getElementById("progressText");
    const logDiv = document.getElementById("log");

    let completed = 0;

    async function testServer(server, index) {
        if (!server.startsWith("http")) server = "http://" + server;
        server = server.replace(/\/$/, "");
        const baseUrl = server + "/player_api.php?username=" + encodeURIComponent(username) + "&password=" + encodeURIComponent(password);

        const startTime = Date.now();
        logDiv.innerHTML += trans.detecting.replace("{0}", index).replace("{1}", servers.length).replace("{2}", server) + "\\n";
        logDiv.scrollTop = logDiv.scrollHeight;

        try {
            const controller = new AbortController();
            const timeout = setTimeout(() => controller.abort(), 15000);

            const resp = await fetch(baseUrl, {
                method: "GET",
                headers: { "Accept": "application/json" },
                signal: controller.signal,
                mode: "cors",
                cache: "no-cache"
            });

            clearTimeout(timeout);
            const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);

            if (resp.status !== 200) {
                logDiv.innerHTML += `→ ${trans.http_error.replace("{0}", resp.status).replace("{1}", elapsed)}\\n\\n`;
            } else {
                const data = await resp.json();
                if (!data || !data.user_info) {
                    logDiv.innerHTML += `→ ${trans.no_userinfo.replace("{0}", elapsed)}\\n\\n`;
                } else {
                    const ui = data.user_info;
                    let exp = ui.exp_date || "永久";
                    if (/^\\d+$/.test(String(exp))) {
                        exp = new Date(parseInt(exp) * 1000).toLocaleString();
                    }
                    const msg = trans.available.replace("{0}", elapsed)
                                             .replace("{1}", ui.status || "Unknown")
                                             .replace("{2}", exp);
                    logDiv.innerHTML += `→ ${msg}\\n\\n`;
                }
            }
        } catch (err) {
            let msg = trans.unknown;
            if (err.name === "AbortError") msg = trans.timeout;
            else if ((err.message || "").toLowerCase().includes("cors") || (err.message || "").includes("fetch")) {
                msg = trans.conn_fail;
            }
            logDiv.innerHTML += `→ ${msg}\\n\\n`;
        }

        logDiv.scrollTop = logDiv.scrollHeight;
        completed++;

        const percent = Math.round((completed / servers.length) * 100);
        progressBar.style.width = percent + "%";
        progressText.textContent = trans.progress_text.replace("{0}", completed)
                                                       .replace("{1}", servers.length)
                                                       .replace("{2}", percent);
    }

    // 执行检测
    (async () => {
        for (let i = 0; i < servers.length; i++) {
            await testServer(servers[i], i + 1);
            await new Promise(r => setTimeout(r, 400));
        }
        logDiv.innerHTML += `\\n${trans.complete.replace("{0}", servers.length)}\\n`;
        logDiv.scrollTop = logDiv.scrollHeight;
    })();
    </script>
    """.format(
        username_str=username_str.replace('"', '\\"'),
        password_str=password_str.replace('"', '\\"'),
        servers_json=json.dumps(servers),
        trans_json=json.dumps(trans)
    )

    st.components.v1.html(js_code, height=680, scrolling=True)

    st.success("✅ 检测已在浏览器中启动！请查看上方实时进度条和检测日志。")

st.caption(trans["footer"])
st.info("💡 检测全部从您的浏览器发出 • 部分服务器因 CORS 限制会显示失败，这是正常现象。")
