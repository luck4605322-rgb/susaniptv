import streamlit as st
import time

# ==================== 多国语言字典（完整版，保持不变） ====================
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
        "footer": "v1.5 简易版 • 只检测是否可用 + 状态 + 过期时间 • 客户端浏览器检测",
        "warning": "请填写服务器列表、账号和密码！",
        "running": "🚀 开始检测 {0} 个服务器...",
        "detecting": "[{0}/{1}] 检测中: {2}\n",
        "complete": "✅ 批量检测完成！共检测 {0} 个服务器。",
        "http_error": "❌ HTTP错误 {0} | 耗时 {1}s",
        "no_userinfo": "❌ 登录失败（无 user_info） | 耗时 {0}s",
        "timeout": "❌ 超时 (>15s)",
        "conn_fail": "❌ 连接失败 (服务器不可达或被阻挡)",
        "unknown": "❌ 未知错误: {0}",
        "available": "✅ 可用 | 耗时 {0}s | 状态: {1} | 过期: {2}",
        "cors_warning": "⚠️ 注意：部分服务器可能因 CORS 策略导致检测失败（浏览器限制）。"
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
        "footer": "v1.5 Simple Version • Only checks availability + status + expiration • Client-side Browser Test",
        "warning": "Please fill in servers, username and password!",
        "running": "🚀 Testing {0} servers...",
        "detecting": "[{0}/{1}] Testing: {2}\n",
        "complete": "✅ Batch test completed! Tested {0} servers.",
        "http_error": "❌ HTTP Error {0} | Time {1}s",
        "no_userinfo": "❌ Login failed (no user_info) | Time {0}s",
        "timeout": "❌ Timeout (>15s)",
        "conn_fail": "❌ Connection failed (unreachable or blocked)",
        "unknown": "❌ Unknown error: {0}",
        "available": "✅ Available | Time {0}s | Status: {1} | Exp: {2}",
        "cors_warning": "⚠️ Note: Some servers may fail due to CORS policy (browser restriction)."
    },
    # 西班牙语和法语保持原样（或按需补充 cors_warning）
    "Español": { ... },  # 你可以复制原字典并添加 "cors_warning"
    "Français": { ... },
}

# ==================== Streamlit 界面 ====================
st.set_page_config(page_title="IPTVNator 批量检测工具 v1.5", layout="wide", page_icon="🚀")

lang = st.selectbox("界面语言 / Language:", options=list(LANGUAGES.keys()), index=0)
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

st.info(trans.get("cors_warning", "⚠️ Some servers may fail due to CORS."))

if st.button(trans["start_btn"], type="primary", use_container_width=True):
    servers = [s.strip() for s in servers_input.strip().splitlines() if s.strip()]
    username_str = username.strip()
    password_str = password.strip()

    if not servers or not username_str or not password_str:
        st.error(trans["warning"])
        st.stop()

    # ==================== 客户端 JavaScript 检测逻辑 ====================
    js_code = f"""
    <script>
    const username = "{username_str}";
    const password = "{password_str}";
    const servers = {servers};
    const trans = {trans};  // 传递翻译字典

    let resultText = trans.running.replace("{{0}}", servers.length) + "\\n\\n";
    const resultDiv = document.createElement("div");
    resultDiv.style.whiteSpace = "pre-wrap";
    resultDiv.style.fontFamily = "monospace";
    resultDiv.style.padding = "10px";
    resultDiv.style.border = "1px solid #ddd";
    resultDiv.style.borderRadius = "5px";
    resultDiv.style.background = "#f9f9f9";
    resultDiv.textContent = resultText;

    // 将结果区域插入 Streamlit 页面
    const container = document.body;
    container.appendChild(resultDiv);

    async function testServer(server, index) {{
        if (!server.startsWith("http")) server = "http://" + server;
        server = server.replace(/\\/$/, "");
        const baseUrl = `${{server}}/player_api.php?username=${{username}}&password=${{password}}`;

        const startTime = Date.now();
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 15000);

        resultText += trans.detecting.replace("{{0}}", index).replace("{{1}}", servers.length).replace("{{2}}", server) + "\\n";
        resultDiv.textContent = resultText;

        try {{
            const resp = await fetch(baseUrl, {{
                method: "GET",
                headers: {{
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "application/json"
                }},
                signal: controller.signal,
                mode: "cors",
                cache: "no-cache"
            }});

            clearTimeout(timeoutId);
            const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);

            if (resp.status !== 200) {{
                const msg = trans.http_error.replace("{{0}}", resp.status).replace("{{1}}", elapsed);
                resultText += `${{server}} → ${{msg}}\\n\\n`;
                resultDiv.textContent = resultText;
                return;
            }}

            const data = await resp.json();
            if (!data || !data.user_info) {{
                const msg = trans.no_userinfo.replace("{{0}}", elapsed);
                resultText += `${{server}} → ${{msg}}\\n\\n`;
                resultDiv.textContent = resultText;
                return;
            }}

            const ui = data.user_info;
            let status = ui.status || "Unknown";
            let exp = ui.exp_date || "永久";
            if (/^\\d+$/.test(exp)) {{
                const date = new Date(parseInt(exp) * 1000);
                exp = date.toLocaleString();
            }}

            const msg = trans.available.replace("{{0}}", elapsed).replace("{{1}}", status).replace("{{2}}", exp);
            resultText += `${{server}} → ${{msg}}\\n\\n`;
            resultDiv.textContent = resultText;

        }} catch (err) {{
            clearTimeout(timeoutId);
            const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
            let msg;
            if (err.name === "AbortError") {{
                msg = trans.timeout;
            }} else if (err.message.includes("Failed to fetch") || err.message.includes("CORS")) {{
                msg = trans.conn_fail;
            }} else {{
                msg = trans.unknown.replace("{{0}}", err.message.substring(0, 80));
            }}
            resultText += `${{server}} → ${{msg}}\\n\\n`;
            resultDiv.textContent = resultText;
        }}
    }}

    // 顺序执行检测
    (async () => {{
        for (let i = 0; i < servers.length; i++) {{
            await testServer(servers[i], i + 1);
            await new Promise(resolve => setTimeout(resolve, 300));  // 避免过快请求
        }}
        resultText += "\\n" + trans.complete.replace("{{0}}", servers.length);
        resultDiv.textContent = resultText;
    }})();
    </script>
    """

    # 使用 components.html 执行客户端 JS（高度可调）
    st.components.v1.html(js_code, height=600, scrolling=True)

st.caption(trans["footer"])
st.markdown("---")
st.info("💡 本版本使用浏览器 JavaScript fetch 从**您的本地网络**进行检测，更真实反映可用性。部分服务器可能因 CORS 限制失败。")
