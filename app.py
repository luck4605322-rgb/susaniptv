import streamlit as st
import json

# ==================== 多国语言字典 ====================
LANGUAGES = {
    "简体中文": {
        "title": "IPTVNator 批量检测工具 v3.0 - 纯浏览器本地检测",
        "username": "用户名:",
        "password": "密码:",
        "servers": "服务器地址（一行一个）:",
        "example": "填入示例",
        "start_btn": "🚀 开始本地浏览器检测",
        "lang_label": "界面语言 / Language:",
        "footer": "v3.0 纯浏览器本地检测 • 请求从您的电脑发出 • 很多服务器会因 CORS 失败",
        "warning": "请填写服务器列表、账号和密码！",
        "cors_warning": "⚠️ 注意：这是纯浏览器本地检测。很多 IPTV 服务器不支持 CORS，会显示“连接失败”。这是浏览器安全限制，不是服务器问题。",
        "running": "🚀 开始从您的浏览器检测 {0} 个服务器...",
        "detecting": "[{0}/{1}] 检测中: {2}",
        "complete": "✅ 浏览器本地检测完成！共检测 {0} 个服务器。",
        "http_error": "❌ HTTP错误 {0} | 耗时 {1}s",
        "no_userinfo": "❌ 登录失败（无 user_info） | 耗时 {0}s",
        "timeout": "❌ 超时 (>15秒)",
        "cors_fail": "❌ 连接失败（浏览器 CORS 限制）",
        "conn_fail": "❌ 连接失败（服务器不可达或被阻挡）",
        "unknown": "❌ 未知错误",
        "available": "✅ 可用 | 耗时 {0}s | 状态: {1} | 过期: {2}"
    },
    "English": {
        "title": "IPTVNator Batch Tester v3.0 - Pure Browser Local Test",
        "username": "Username:",
        "password": "Password:",
        "servers": "Server Addresses (one per line):",
        "example": "Load Example",
        "start_btn": "🚀 Start Browser Local Test",
        "lang_label": "Interface Language:",
        "footer": "v3.0 Pure Browser Local Detection • Requests from your computer",
        "warning": "Please fill in servers, username and password!",
        "cors_warning": "⚠️ This is pure browser local test. Many IPTV servers will show 'Connection failed' due to CORS policy.",
        "running": "🚀 Starting local browser test for {0} servers...",
        "detecting": "[{0}/{1}] Testing: {2}",
        "complete": "✅ Browser local test completed! Tested {0} servers.",
        "http_error": "❌ HTTP Error {0} | Time {1}s",
        "no_userinfo": "❌ Login failed (no user_info) | Time {0}s",
        "timeout": "❌ Timeout (>15s)",
        "cors_fail": "❌ Connection failed (Browser CORS restriction)",
        "conn_fail": "❌ Connection failed (Server unreachable)",
        "unknown": "❌ Unknown error",
        "available": "✅ Available | Time {0}s | Status: {1} | Exp: {2}"
    }
}

st.set_page_config(page_title="IPTVNator 纯浏览器检测", layout="wide", page_icon="🚀")

lang = st.selectbox(LANGUAGES["简体中文"]["lang_label"], options=list(LANGUAGES.keys()), index=0)
trans = LANGUAGES[lang]

st.title("🚀 " + trans["title"])

col1, col2 = st.columns([2, 1])
with col1:
    username = st.text_input(trans["username"], placeholder="username")
    password = st.text_input(trans["password"], type="password", placeholder="password")
with col2:
    if st.button(trans["example"], use_container_width=True):
        st.session_state["servers"] = "http://line.uhdnovus.com\nhttp://onee.pro\nhttp://line.proswifts.com"

servers_input = st.text_area(
    trans["servers"],
    height=180,
    value=st.session_state.get("servers", ""),
    placeholder="一行一个服务器地址"
)

st.warning(trans["cors_warning"])

if st.button(trans["start_btn"], type="primary", use_container_width=True):
    servers = [s.strip() for s in servers_input.strip().splitlines() if s.strip()]
    username_str = username.strip()
    password_str = password.strip()

    if not servers or not username_str or not password_str:
        st.error(trans["warning"])
        st.stop()

    username_escaped = username_str.replace('\\', '\\\\').replace('"', '\\"')
    password_escaped = password_str.replace('\\', '\\\\').replace('"', '\\"')

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: system-ui, sans-serif; background: #f8f9fa; padding: 20px; }}
            .container {{ max-width: 1000px; margin: auto; background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 25px rgba(0,0,0,0.1); }}
            .progress-container {{ height: 32px; background: #e9ecef; border-radius: 8px; overflow: hidden; margin: 20px 0; }}
            .progress-bar {{ height: 100%; background: linear-gradient(90deg, #28a745, #20c997); width: 0%; transition: width 0.5s ease; }}
            .log {{ background: #f8f9fa; border: 1px solid #dee2e6; padding: 16px; height: 520px; overflow-y: auto; font-family: Consolas, monospace; white-space: pre-wrap; font-size: 14px; line-height: 1.6; }}
            .success {{ color: #28a745; font-weight: bold; }}
            .error {{ color: #dc3545; }}
            .warning {{ color: #ffc107; font-weight: bold; }}
        </style>
    </head>
    <body>
    <div class="container">
        <h2>{trans["running"].replace("{0}", str(len(servers)))}</h2>
        <div class="progress-container">
            <div id="progressBar" class="progress-bar"></div>
        </div>
        <div id="progressText" style="text-align:center; font-weight:bold; margin: 10px 0;">0/{len(servers)} (0%)</div>
        <div id="log" class="log"></div>
    </div>

    <script>
    const username = "{username_escaped}";
    const password = "{password_escaped}";
    const servers = {json.dumps(servers)};

    let completed = 0;
    const logDiv = document.getElementById("log");
    const progressBar = document.getElementById("progressBar");
    const progressText = document.getElementById("progressText");

    async function testServer(server, index) {{
        if (!server.startsWith("http")) server = "http://" + server;
        server = server.replace(/\/$/, "");
        const baseUrl = server + "/player_api.php?username=" + encodeURIComponent(username) + "&password=" + encodeURIComponent(password);

        const startTime = Date.now();
        logDiv.innerHTML += `${{trans["detecting"].replace("{0}", index).replace("{1}", servers.length).replace("{2}", server)}}\\n`;
        logDiv.scrollTop = logDiv.scrollHeight;

        try {{
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 15000);

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
                logDiv.innerHTML += `→ <span class="error">${{trans["http_error"].replace("{0}", resp.status).replace("{1}", elapsed)}}</span>\\n\\n`;
            }} else {{
                const data = await resp.json();
                if (!data || !data.user_info) {{
                    logDiv.innerHTML += `→ <span class="error">${{trans["no_userinfo"].replace("{0}", elapsed)}}</span>\\n\\n`;
                }} else {{
                    const ui = data.user_info;
                    let exp = ui.exp_date || "永久";
                    if (/^\\d+$/.test(String(exp))) {{
                        exp = new Date(parseInt(exp) * 1000).toLocaleString();
                    }}
                    const msg = trans["available"].replace("{0}", elapsed).replace("{1}", ui.status || "Unknown").replace("{2}", exp);
                    logDiv.innerHTML += `→ <span class="success">${{msg}}</span>\\n\\n`;
                }}
            }}
        }} catch (err) {{
            clearTimeout(timeoutId);
            const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
            let msg = `<span class="error">${{trans["unknown"]}}</span>`;

            if (err.name === "AbortError") {{
                msg = `<span class="error">${{trans["timeout"]}}</span>`;
            }} else if (err.message && (err.message.includes("CORS") || err.message.includes("Failed to fetch") || err.message.includes("NetworkError"))) {{
                msg = `<span class="warning">${{trans["cors_fail"]}}</span>`;
            }} else if (err.message && err.message.includes("fetch")) {{
                msg = `<span class="error">${{trans["conn_fail"]}}</span>`;
            }}

            logDiv.innerHTML += `→ ${{msg}} | 耗时 ${{elapsed}}s\\n\\n`;
        }}

        logDiv.scrollTop = logDiv.scrollHeight;
        completed++;

        const percent = Math.round((completed / servers.length) * 100);
        progressBar.style.width = percent + "%";
        progressText.textContent = `${{completed}}/${{servers.length}} (${{percent}}%)`;
    }}

    // 开始检测
    (async () => {{
        for (let i = 0; i < servers.length; i++) {{
            await testServer(servers[i], i + 1);
            await new Promise(r => setTimeout(r, 450));  // 避免请求过密
        }}
        logDiv.innerHTML += `\\n${{trans["complete"].replace("{0}", servers.length)}}\\n`;
        logDiv.scrollTop = logDiv.scrollHeight;
    }})();
    </script>
    </body>
    </html>
    """

    st.components.v1.html(html_code, height=750, scrolling=True)

st.caption(trans["footer"])
st.info("💡 本版本所有检测请求均从**您的本地浏览器**发出，真实反映您当前网络环境。但很多 IPTV 服务器会因 CORS 被浏览器阻挡而失败。")
