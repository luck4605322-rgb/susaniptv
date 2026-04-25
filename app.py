import streamlit as st
import json

LANGUAGES = {
    "简体中文": {
        "title": "IPTVNator 批量检测工具 v2.0 - 网页版",
        "username": "用户名:",
        "password": "密码:",
        "servers": "服务器地址（一行一个）:",
        "example": "填入示例",
        "start_btn": "🚀 开始批量检测",
        "lang_label": "界面语言 / Language:",
        "footer": "v2.0 网页版 • 受浏览器CORS限制 • 推荐配合本地EXE使用",
        "warning": "请填写服务器列表、账号和密码！",
        "cors_big_warning": "⚠️ 浏览器网页版检测容易出现大量“连接失败”或“未知错误”，这是浏览器CORS安全限制导致的。\n实际服务器可能可用，建议使用本地Tkinter EXE版本获得更准确结果。",
        "running": "🚀 开始检测 {0} 个服务器...（网页版受CORS影响）",
    },
    "English": {
        "title": "IPTVNator Batch Tester v2.0 - Web Version",
        "username": "Username:",
        "password": "Password:",
        "servers": "Server Addresses (one per line):",
        "example": "Load Example",
        "start_btn": "🚀 Start Batch Test",
        "lang_label": "Interface Language:",
        "footer": "v2.0 Web Version • Affected by Browser CORS • Recommend Local EXE",
        "warning": "Please fill in servers, username and password!",
        "cors_big_warning": "⚠️ Web version often shows many 'Connection failed' or 'Unknown error' due to browser CORS policy.\nThe server may actually be available. Use Local Tkinter EXE for accurate results.",
        "running": "🚀 Testing {0} servers... (Limited by browser CORS)",
    },
}

st.set_page_config(page_title="IPTVNator 批量检测工具 v2.0", layout="wide", page_icon="🚀")

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

st.error(trans["cors_big_warning"])

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
            body {{ font-family: system-ui, Arial, sans-serif; background: #f8f9fa; padding: 20px; }}
            .panel {{ max-width: 1000px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); padding: 25px; }}
            .progress-container {{ height: 30px; background: #e0e0e0; border-radius: 8px; overflow: hidden; margin: 20px 0; }}
            .progress-bar {{ height: 100%; background: linear-gradient(90deg, #28a745, #17a2b8); width: 0%; transition: width 0.4s; }}
            .log {{ background: #f1f3f5; border: 1px solid #ced4da; padding: 15px; height: 520px; overflow-y: auto; font-family: Consolas, monospace; font-size: 14px; white-space: pre-wrap; line-height: 1.5; }}
            .success {{ color: #28a745; }}
            .error {{ color: #dc3545; }}
            .warning {{ color: #ffc107; }}
        </style>
    </head>
    <body>
    <div class="panel">
        <h2>🚀 {trans["running"].replace("{0}", str(len(servers)))}</h2>
        <div class="progress-container">
            <div id="progress" class="progress-bar"></div>
        </div>
        <div id="progressText" style="text-align:center; font-weight: bold; margin-bottom: 15px;">0/{len(servers)} (0%)</div>
        <div id="log" class="log"></div>
    </div>

    <script>
    const username = "{username_escaped}";
    const password = "{password_escaped}";
    const servers = {json.dumps(servers)};

    let completed = 0;
    const logDiv = document.getElementById("log");
    const progressBar = document.getElementById("progress");
    const progressText = document.getElementById("progressText");

    async function testServer(server, index) {{
        if (!server.startsWith("http")) server = "http://" + server;
        server = server.replace(/\/$/, "");
        const baseUrl = `${{server}}/player_api.php?username=${{encodeURIComponent(username)}}&password=${{encodeURIComponent(password)}}`;

        const startTime = Date.now();
        logDiv.innerHTML += `[${{index}}/${{servers.length}}] 检测中 → ${{server}}\\n`;
        logDiv.scrollTop = logDiv.scrollHeight;

        try {{
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 15000);

            const resp = await fetch(baseUrl, {{
                method: 'GET',
                headers: {{ 'Accept': 'application/json' }},
                signal: controller.signal,
                mode: 'cors',
                cache: 'no-cache'
            }});

            clearTimeout(timeoutId);
            const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);

            if (resp.status !== 200) {{
                logDiv.innerHTML += `→ <span class="error">❌ HTTP错误 ${{resp.status}} | 耗时 ${{elapsed}}s</span>\\n\\n`;
            }} else {{
                const data = await resp.json();
                if (!data || !data.user_info) {{
                    logDiv.innerHTML += `→ <span class="error">❌ 登录失败（无 user_info）</span> | 耗时 ${{elapsed}}s\\n\\n`;
                }} else {{
                    const ui = data.user_info;
                    let exp = ui.exp_date || "永久";
                    if (/^\\d+$/.test(String(exp))) {{
                        exp = new Date(parseInt(exp) * 1000).toLocaleString();
                    }}
                    logDiv.innerHTML += `→ <span class="success">✅ 可用 | 耗时 ${{elapsed}}s | 状态: ${{ui.status || "Unknown"}} | 过期: ${{exp}}</span>\\n\\n`;
                }}
            }}
        }} catch (err) {{
            clearTimeout(timeoutId);
            const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
            let msg = `<span class="error">❌ 未知错误</span>`;
            
            if (err.name === "AbortError") {{
                msg = `<span class="error">❌ 超时 (>15s)</span>`;
            }} else if (err.message.includes("CORS") || err.message.includes("Failed to fetch") || err.message.includes("NetworkError")) {{
                msg = `<span class="warning">❌ 连接失败（浏览器CORS限制）</span>`;
            }} else if (err.message.includes("JSON")) {{
                msg = `<span class="error">❌ 返回内容不是JSON</span>`;
            }}
            
            logDiv.innerHTML += `→ ${{msg}} | 耗时 ${{elapsed}}s\\n\\n`;
        }}

        logDiv.scrollTop = logDiv.scrollHeight;
        completed++;

        const percent = Math.round((completed / servers.length) * 100);
        progressBar.style.width = percent + "%";
        progressText.textContent = `${{completed}}/${{servers.length}} (${{percent}}%)`;
    }}

    // 执行检测
    (async () => {{
        for (let i = 0; i < servers.length; i++) {{
            await testServer(servers[i], i + 1);
            await new Promise(resolve => setTimeout(resolve, 500));
        }}
        logDiv.innerHTML += `\\n✅ 网页版检测完成（受CORS影响较大，建议使用本地EXE版本）\\n`;
        logDiv.scrollTop = logDiv.scrollHeight;
    }})();
    </script>
    </body>
    </html>
    """

    st.components.v1.html(html_code, height=780, scrolling=True)

st.caption(trans["footer"])
st.info("💡 **提示**：网页版主要用于演示和快速测试。**最准确的结果依然推荐使用本地 Tkinter EXE 版本**。")
