import streamlit as st
import json

# ==================== 多国语言字典（已完整修复） ====================
LANGUAGES = {
    "简体中文": {
        "title": "IPTVNator 批量检测工具 v1.5 - 简易可用性检测",
        "username": "用户名:",
        "password": "密码:",
        "servers": "服务器地址（一行一个）:",
        "example": "填入示例",
        "start_btn": "🚀 开始批量检测",
        "lang_label": "界面语言 / Language:",
        "result_label": "检测结果（实时）:",
        "footer": "v1.5 简易版 • 客户端浏览器检测 • 带进度条",
        "warning": "请填写服务器列表、账号和密码！",
        "running": "🚀 开始检测 {0} 个服务器...",
        "detecting": "[{0}/{1}] 检测中: {2}",
        "complete": "✅ 批量检测完成！共检测 {0} 个服务器。",
        "http_error": "❌ HTTP错误 {0} | 耗时 {1}s",
        "no_userinfo": "❌ 登录失败（无 user_info） | 耗时 {0}s",
        "timeout": "❌ 超时 (>15s)",
        "conn_fail": "❌ 连接失败 (服务器不可达或被阻挡)",
        "unknown": "❌ 未知错误: {0}",
        "available": "✅ 可用 | 耗时 {0}s | 状态: {1} | 过期: {2}",
        "cors_warning": "⚠️ 注意：部分服务器可能因 CORS 策略导致检测失败（浏览器安全限制）。",
        "progress": "进度：{0}/{1} ({2}%)"
    },
    "English": {
        "title": "IPTVNator Batch Tester v1.5 - Simple Availability Check",
        "username": "Username:",
        "password": "Password:",
        "servers": "Server Addresses (one per line):",
        "example": "Load Example",
        "start_btn": "🚀 Start Batch Test",
        "lang_label": "Interface Language:",
        "result_label": "Test Results (Live):",
        "footer": "v1.5 Simple Version • Client-side Browser Test • With Progress Bar",
        "warning": "Please fill in servers, username and password!",
        "running": "🚀 Testing {0} servers...",
        "detecting": "[{0}/{1}] Testing: {2}",
        "complete": "✅ Batch test completed! Tested {0} servers.",
        "http_error": "❌ HTTP Error {0} | Time {1}s",
        "no_userinfo": "❌ Login failed (no user_info) | Time {0}s",
        "timeout": "❌ Timeout (>15s)",
        "conn_fail": "❌ Connection failed (unreachable or blocked)",
        "unknown": "❌ Unknown error: {0}",
        "available": "✅ Available | Time {0}s | Status: {1} | Exp: {2}",
        "cors_warning": "⚠️ Note: Some servers may fail due to CORS policy (browser restriction).",
        "progress": "Progress: {0}/{1} ({2}%)"
    },
    "Español": {
        "title": "Herramienta de Prueba IPTVNator v1.5 - Comprobación Simple",
        "username": "Usuario:",
        "password": "Contraseña:",
        "servers": "Direcciones del servidor (una por línea):",
        "example": "Cargar ejemplo",
        "start_btn": "🚀 Iniciar prueba por lotes",
        "lang_label": "Idioma de la interfaz:",
        "result_label": "Resultados de la prueba (en vivo):",
        "footer": "v1.5 Versión Simple • Detección del lado del cliente • Con barra de progreso",
        "warning": "¡Por favor complete servidores, usuario y contraseña!",
        "running": "🚀 Probando {0} servidores...",
        "detecting": "[{0}/{1}] Probando: {2}",
        "complete": "✅ ¡Prueba por lotes completada! Se probaron {0} servidores.",
        "http_error": "❌ Error HTTP {0} | Tiempo {1}s",
        "no_userinfo": "❌ Fallo de inicio de sesión (sin user_info) | Tiempo {0}s",
        "timeout": "❌ Tiempo de espera agotado (>15s)",
        "conn_fail": "❌ Fallo de conexión (servidor inaccesible o bloqueado)",
        "unknown": "❌ Error desconocido: {0}",
        "available": "✅ Disponible | Tiempo {0}s | Estado: {1} | Expira: {2}",
        "cors_warning": "⚠️ Nota: Algunos servidores pueden fallar por política CORS (restricción del navegador).",
        "progress": "Progreso: {0}/{1} ({2}%)"
    },
    "Français": {
        "title": "Outil de Test IPTVNator v1.5 - Vérification Simple",
        "username": "Nom d'utilisateur:",
        "password": "Mot de passe:",
        "servers": "Adresses du serveur (une par ligne):",
        "example": "Charger exemple",
        "start_btn": "🚀 Lancer le test par lots",
        "lang_label": "Langue de l'interface:",
        "result_label": "Résultats du test (temps réel):",
        "footer": "v1.5 Version Simple • Détection côté client • Avec barre de progression",
        "warning": "Veuillez remplir les serveurs, nom d'utilisateur et mot de passe !",
        "running": "🚀 Test de {0} serveurs...",
        "detecting": "[{0}/{1}] Test en cours: {2}",
        "complete": "✅ Test par lots terminé ! {0} serveurs testés.",
        "http_error": "❌ Erreur HTTP {0} | Temps {1}s",
        "no_userinfo": "❌ Échec de connexion (pas de user_info) | Temps {0}s",
        "timeout": "❌ Délai dépassé (>15s)",
        "conn_fail": "❌ Échec de connexion (serveur inaccessible ou bloqué)",
        "unknown": "❌ Erreur inconnue: {0}",
        "available": "✅ Disponible | Temps {0}s | Statut: {1} | Expiration: {2}",
        "cors_warning": "⚠️ Note : Certains serveurs peuvent échouer en raison de la politique CORS (restriction du navigateur).",
        "progress": "Progression: {0}/{1} ({2}%)"
    }
}

# ==================== Streamlit 界面 ====================
st.set_page_config(page_title="IPTVNator 批量检测工具 v1.5", layout="wide", page_icon="🚀")

lang = st.selectbox(LANGUAGES["简体中文"]["lang_label"], options=list(LANGUAGES.keys()), index=0)
trans = LANGUAGES[lang]

st.title("🚀 " + trans["title"])

col1, col2 = st.columns([2, 1])
with col1:
    username = st.text_input(trans["username"], placeholder="username")
    password = st.text_input(trans["password"], type="password", placeholder="password")
with col2:
    if st.button(trans["example"], use_container_width=True):
        st.session_state["servers"] = "http://example.com:8080\nhttp://test.tv:12345\nhttp://backup.server:9999"

servers_input = st.text_area(
    trans["servers"],
    height=200,
    value=st.session_state.get("servers", ""),
    placeholder="一行一个服务器地址\nhttp://example.com:8080"
)

st.info(trans.get("cors_warning", ""))

if st.button(trans["start_btn"], type="primary", use_container_width=True):
    servers = [s.strip() for s in servers_input.strip().splitlines() if s.strip()]
    username_str = username.strip()
    password_str = password.strip()

    if not servers or not username_str or not password_str:
        st.error(trans["warning"])
        st.stop()

    # 显示区域
    status_placeholder = st.empty()
    progress_bar = st.progress(0)
    result_placeholder = st.empty()

    status_placeholder.info(trans["running"].format(len(servers)))

    # ==================== 客户端 JavaScript（带进度条） ====================
    js_code = f"""
    <script>
    const username = "{username_str.replace('"', '\\"')}";
    const password = "{password_str.replace('"', '\\"')}";
    const servers = {json.dumps(servers)};
    const trans = {json.dumps(trans)};

    let resultText = "";
    let completed = 0;
    const total = servers.length;

    const resultDiv = document.createElement("div");
    resultDiv.style.whiteSpace = "pre-wrap";
    resultDiv.style.fontFamily = "monospace";
    resultDiv.style.padding = "12px";
    resultDiv.style.border = "1px solid #ddd";
    resultDiv.style.borderRadius = "6px";
    resultDiv.style.background = "#f8f9fa";
    resultDiv.style.marginTop = "10px";
    document.body.appendChild(resultDiv);

    async function testServer(server, index) {{
        if (!server.startsWith("http")) server = "http://" + server;
        server = server.replace(/\\/$/, "");
        const baseUrl = `${{server}}/player_api.php?username=${{username}}&password=${{password}}`;

        const startTime = Date.now();
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 15000);

        resultText += trans.detecting.replace("{{0}}", index).replace("{{1}}", total).replace("{{2}}", server) + "\\n";
        resultDiv.textContent = resultText;

        // 更新进度
        window.parent.postMessage({{type: "progress", completed: completed, total: total}}, "*");

        try {{
            const resp = await fetch(baseUrl, {{
                method: "GET",
                headers: {{ "Accept": "application/json" }},
                signal: controller.signal,
                mode: "cors",
                cache: "no-cache"
            }});

            clearTimeout(timeoutId);
            const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);

            if (resp.status !== 200) {{
                resultText += `${{server}} → ${{trans.http_error.replace("{{0}}", resp.status).replace("{{1}}", elapsed)}}\\n\\n`;
            }} else {{
                const data = await resp.json();
                if (!data || !data.user_info) {{
                    resultText += `${{server}} → ${{trans.no_userinfo.replace("{{0}}", elapsed)}}\\n\\n`;
                }} else {{
                    const ui = data.user_info;
                    let exp = ui.exp_date || "永久";
                    if (/^\\d+$/.test(String(exp))) {{
                        const date = new Date(parseInt(exp) * 1000);
                        exp = date.toLocaleString();
                    }}
                    const msg = trans.available.replace("{{0}}", elapsed)
                                             .replace("{{1}}", ui.status || "Unknown")
                                             .replace("{{2}}", exp);
                    resultText += `${{server}} → ${{msg}}\\n\\n`;
                }}
            }}
        }} catch (err) {{
            clearTimeout(timeoutId);
            let msg = trans.unknown.replace("{{0}}", (err.message || "").substring(0, 80));
            if (err.name === "AbortError") msg = trans.timeout;
            else if ((err.message || "").includes("fetch") || (err.message || "").includes("CORS")) msg = trans.conn_fail;
            resultText += `${{server}} → ${{msg}}\\n\\n`;
        }}

        resultDiv.textContent = resultText;
        completed++;

        window.parent.postMessage({{
            type: "progress",
            completed: completed,
            total: total
        }}, "*");
    }}

    (async () => {{
        for (let i = 0; i < servers.length; i++) {{
            await testServer(servers[i], i + 1);
            await new Promise(r => setTimeout(r, 350));
        }}
        resultText += "\\n" + trans.complete.replace("{{0}}", total);
        resultDiv.textContent = resultText;
        window.parent.postMessage({{ type: "complete" }}, "*");
    }})();
    </script>
    """

    st.components.v1.html(js_code, height=750, scrolling=True)

    st.success("✅ 检测已启动！进度条和结果将实时更新。")

st.caption(trans["footer"])
st.markdown("---")
st.info("💡 所有检测请求均从**您的浏览器网络**发出 • 进度条实时更新")
