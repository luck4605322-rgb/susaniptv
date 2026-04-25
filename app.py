import streamlit as st
import json

# ==================== 多国语言字典 ====================
LANGUAGES = {
    "简体中文": {
        "title": "IPTVNator 批量检测工具 v1.9 - 浏览器端",
        "username": "用户名:",
        "password": "密码:",
        "servers": "服务器地址（一行一个）:",
        "example": "填入示例",
        "start_btn": "🚀 开始批量检测",
        "lang_label": "界面语言 / Language:",
        "footer": "v1.9 • 浏览器端检测 • 受CORS影响 • 推荐使用本地EXE版",
        "warning": "请填写服务器列表、账号和密码！",
        "cors_warning": "⚠️ 重要：浏览器检测经常显示“连接失败”，但本地EXE可能显示可用。这是浏览器CORS限制导致的，并非服务器真的不可用。",
        "running": "🚀 正在检测 {0} 个服务器...（受浏览器限制影响）",
    },
    "English": {
        "title": "IPTVNator Batch Tester v1.9 - Browser Side",
        "username": "Username:",
        "password": "Password:",
        "servers": "Server Addresses (one per line):",
        "example": "Load Example",
        "start_btn": "🚀 Start Batch Test",
        "lang_label": "Interface Language:",
        "footer": "v1.9 • Browser Detection • Affected by CORS • Recommend Local EXE",
        "warning": "Please fill in servers, username and password!",
        "cors_warning": "⚠️ Important: Browser version often shows 'Connection failed' even if server is available. This is due to CORS policy. Use Local EXE for accurate results.",
        "running": "🚀 Testing {0} servers... (Limited by browser CORS)",
    },
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
    placeholder="http://your-server.com:8080"
)

st.warning(trans["cors_warning"])
st.info("💡 **强烈推荐**：使用本地 Tkinter EXE 版本进行准确检测（不受 CORS 限制）。网页版主要用于快速预览。")

if st.button(trans["start_btn"], type="primary", use_container_width=True):
    servers = [s.strip() for s in servers_input.strip().splitlines() if s.strip()]
    username_str = username.strip()
    password_str = password.strip()

    if not servers or not username_str or not password_str:
        st.error(trans["warning"])
        st.stop()

    username_escaped = username_str.replace('\\', '\\\\').replace('"', '\\"')
    password_escaped = password_str.replace('\\', '\\\\').replace('"', '\\"')

    detection_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: system-ui, sans-serif; background: #f4f6f9; padding: 20px; }}
            .container {{ max-width: 950px; margin: auto; background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 25px rgba(0,0,0,0.12); }}
            .progress-container {{ height: 32px; background: #e9ecef; border-radius: 8px; overflow: hidden; margin: 20px 0; }}
            .progress-bar {{ height: 100%; background: linear-gradient(90deg, #28a745, #20c997); width: 0%; transition: width 0.5s ease; }}
            .log {{ background: #f8f9fa; border: 1px solid #dee2e6; padding: 16px; height: 480px; overflow-y: auto; font-family: Consolas, monospace; white-space: pre-wrap; font-size: 14px; line-height: 1.55; }}
            .note {{ color: #d32f2f; font-size: 14px; margin: 10px 0; }}
        </style>
    </head>
    <body>
    <div class="container">
        <h2>🚀 {trans.get("running", "").replace("{0}", str(len(servers)))}</h2>
        <div class="note">⚠️ 浏览器检测受 CORS 限制，部分“连接失败”可能是假阴性</div>
        
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
                    if (/^\\d+$/.test(String(exp))) exp = new Date(parseInt(exp)*1000).toLocaleString();
                    const msg = `✅ 可用 | 耗时 ${{elapsed}}s | 状态: ${{ui.status || "Unknown"}} | 过期: ${{exp}}`;
                    document.getElementById("log").innerHTML += `→ ${{msg}}\\n\\n`;
                }}
            }}
        }} catch (err) {{
            let msg = "❌ 未知错误";
            if (err.name === "AbortError") msg = "❌ 超时 (>15秒)";
            else if ((err.message || "").toLowerCase().includes("cors") || (err.message || "").includes("failed to fetch")) {{
                msg = "❌ 连接失败（很可能被浏览器CORS策略阻挡）";
            }}
            document.getElementById("log").innerHTML += `→ ${{msg}}\\n\\n`;
        }}

        document.getElementById("log").scrollTop = document.getElementById("log").scrollHeight;
        completed++;

        const percent = Math.round((completed / servers.length) * 100);
        document.getElementById("progressBar").style.width = percent + "%";
        document.getElementById("progressText").textContent = `${{completed}}/${{servers.length}} (${{percent}}%)`;
    }}

    (async () => {{
        for (let i = 0; i < servers.length; i++) {{
            await testServer(servers[i], i + 1);
            await new Promise(r => setTimeout(r, 450));
        }}
        document.getElementById("log").innerHTML += `\\n✅ 检测结束（浏览器版结果受CORS影响较大）\\n`;
    }})();
    </script>
    </body>
    </html>
    """

    st.components.v1.html(detection_html, height=750, scrolling=True)

st.caption(trans["footer"])
st.info("💡 **最佳实践**：网页版适合快速测试，本地 Tkinter EXE 版本结果更准确（推荐生成 EXE 使用）。")
