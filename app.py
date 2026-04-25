import streamlit as st
import json

# ==================== 多国语言 ====================
LANGUAGES = {
    "简体中文": {
        "title": "IPTVNator 批量检测工具 v3.5 - 纯浏览器本地检测",
        "username": "用户名:",
        "password": "密码:",
        "servers": "服务器地址（一行一个）:",
        "example": "填入示例",
        "start_btn": "🚀 开始本地浏览器检测",
        "lang_label": "界面语言 / Language:",
        "footer": "v3.5 纯浏览器本地检测 • 已优化界面显示",
        "warning": "请填写服务器列表、账号和密码！",
        "cors_warning": "⚠️ 纯浏览器本地检测 • 很多服务器会因 CORS 显示连接失败（浏览器安全限制）",
        "running": "🚀 从您的浏览器开始检测 {0} 个服务器...",
        "detecting": "[{0}/{1}] 检测中: {2}",
        "complete": "✅ 浏览器本地检测完成！共检测 {0} 个服务器。",
        "http_error": "❌ HTTP错误 {0} | 耗时 {1}s",
        "no_userinfo": "❌ 登录失败（无 user_info） | 耗时 {0}s",
        "timeout": "❌ 超时 (>15秒)",
        "cors_fail": "❌ 连接失败（浏览器 CORS 限制）",
        "conn_fail": "❌ 连接失败（服务器不可达）",
        "unknown": "❌ 未知错误",
        "available": "✅ 可用 | 耗时 {0}s | 状态: {1} | 过期: {2}"
    },
    "English": {
        "title": "IPTVNator Batch Tester v3.5 - Pure Browser Local",
        "username": "Username:",
        "password": "Password:",
        "servers": "Server Addresses (one per line):",
        "example": "Load Example",
        "start_btn": "🚀 Start Browser Local Test",
        "lang_label": "Interface Language:",
        "footer": "v3.5 Pure Browser Local Detection",
        "warning": "Please fill in servers, username and password!",
        "cors_warning": "⚠️ Pure browser local test. Many servers fail due to CORS.",
        "running": "🚀 Starting browser local test for {0} servers...",
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

st.set_page_config(page_title="IPTVNator 纯浏览器检测 v3.5", layout="wide", page_icon="🚀")

lang = st.selectbox(LANGUAGES["简体中文"]["lang_label"], options=list(LANGUAGES.keys()), index=0)
trans = LANGUAGES[lang]

st.title("🚀 " + trans["title"])

col1, col2 = st.columns([2, 1])
with col1:
    username = st.text_input(trans["username"], placeholder="username")
    password = st.text_input(trans["password"], type="password", placeholder="password")
with col2:
    if st.button(trans["example"], use_container_width=True):
        st.session_state["servers"] = "http://line.uhdnovus.com\nhttp://onee.pro"

servers_input = st.text_area(trans["servers"], height=180, 
                             value=st.session_state.get("servers", ""), 
                             placeholder="一行一个服务器地址")

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
    running_text = trans["running"].replace("{0}", str(len(servers)))

    detection_html = f"""
    <script>
    const username = "{username_escaped}";
    const password = "{password_escaped}";
    const servers = {json.dumps(servers)};
    const trans = {json.dumps(trans)};

    let completed = 0;

    // 创建独立检测面板
    document.body.innerHTML = `
        <div style="padding:30px; max-width:1100px; margin:0 auto;">
            <div style="background:white; padding:30px; border-radius:16px; box-shadow:0 8px 30px rgba(0,0,0,0.15);">
                <h2 style="margin-top:0; color:#28a745;">🚀 ${{running_text}}</h2>
                
                <div style="height:38px; background:#e9ecef; border-radius:10px; overflow:hidden; margin:25px 0;">
                    <div id="progressBar" style="height:100%; background:linear-gradient(90deg,#28a745,#20c997); width:0%; transition:width 0.6s ease;"></div>
                </div>
                <div id="progressText" style="text-align:center; font-weight:bold; font-size:18px; margin-bottom:20px;">0/${{servers.length}} (0%)</div>
                
                <div id="log" style="background:#f8f9fa; border:2px solid #ddd; padding:20px; height:520px; overflow-y:auto; 
                                    font-family:Consolas,monospace; white-space:pre-wrap; font-size:14.5px; line-height:1.65; border-radius:10px;"></div>
            </div>
        </div>
    `;

    const progressBar = document.getElementById("progressBar");
    const progressText = document.getElementById("progressText");
    const logDiv = document.getElementById("log");

    async function testServer(server, index) {{
        if (!server.startsWith("http")) server = "http://" + server;
        server = server.replace(/\/$/, "");
        const baseUrl = server + "/player_api.php?username=" + encodeURIComponent(username) + "&password=" + encodeURIComponent(password);

        const startTime = Date.now();
        logDiv.innerHTML += trans.detecting.replace("{0}", index).replace("{1}", servers.length).replace("{2}", server) + "\\n";
        logDiv.scrollTop = logDiv.scrollHeight;

        try {{
            const controller = new AbortController();
            const id = setTimeout(() => controller.abort(), 15000);

            const resp = await fetch(baseUrl, {{
                method: "GET",
                headers: {{ "Accept": "application/json" }},
                signal: controller.signal,
                mode: "cors"
            }});

            clearTimeout(id);
            const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);

            if (resp.status !== 200) {{
                logDiv.innerHTML += `→ ❌ HTTP错误 ${{resp.status}} | 耗时 ${{elapsed}}s\\n\\n`;
            }} else {{
                const data = await resp.json();
                if (!data || !data.user_info) {{
                    logDiv.innerHTML += `→ ❌ 登录失败 | 耗时 ${{elapsed}}s\\n\\n`;
                }} else {{
                    const ui = data.user_info;
                    let exp = ui.exp_date || "永久";
                    if (/^\\d+$/.test(String(exp))) exp = new Date(parseInt(exp)*1000).toLocaleString();
                    logDiv.innerHTML += `→ ✅ 可用 | 耗时 ${{elapsed}}s | 状态: ${{ui.status || "Unknown"}} | 过期: ${{exp}}\\n\\n`;
                }}
            }}
        }} catch (err) {{
            const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
            let msg = "❌ 未知错误";
            if (err.name === "AbortError") msg = trans.timeout;
            else if (err.message.includes("CORS") || err.message.includes("Failed to fetch")) msg = trans.cors_fail;
            else msg = trans.conn_fail;
            logDiv.innerHTML += `→ ${{msg}} | 耗时 ${{elapsed}}s\\n\\n`;
        }}

        logDiv.scrollTop = logDiv.scrollHeight;
        completed++;

        const percent = Math.round((completed / servers.length) * 100);
        progressBar.style.width = percent + "%";
        progressText.textContent = completed + "/" + servers.length + " (" + percent + "%)";
        
        await new Promise(r => setTimeout(r, 600));
    }}

    (async () => {{
        for (let i = 0; i < servers.length; i++) {{
            await testServer(servers[i], i + 1);
        }}
        logDiv.innerHTML += "\\n" + trans.complete.replace("{0}", servers.length) + "\\n";
        logDiv.scrollTop = logDiv.scrollHeight;
    }})();
    </script>
    """

    st.components.v1.html(detection_html, height=820, scrolling=True)

st.caption(trans["footer"])
st.info("💡 如果还是没有看到进度条，请尝试：1. 刷新页面 2. 使用 Chrome 浏览器 3. 清空缓存后重试")
