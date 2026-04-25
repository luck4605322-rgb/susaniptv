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
        "cors_warning": "⚠️ 注意：很多 IPTV 服务器不支持 CORS，可能会显示连接失败。这是浏览器安全限制，无法完全避免。",
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
    "Español": { ... },   # 如果你需要完整西班牙语和法语，可以告诉我，我再补充
    "Français": { ... },
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

servers_input = st.text_area(trans["servers"], height=180, 
                             value=st.session_state.get("servers", ""),
                             placeholder="http://your-server.com:8080")

st.warning(trans["cors_warning"])

if st.button(trans["start_btn"], type="primary", use_container_width=True):
    servers = [s.strip() for s in servers_input.strip().splitlines() if s.strip()]
    if not servers or not username.strip() or not password.strip():
        st.error(trans["warning"])
        st.stop()

    # ==================== 纯前端 JS 检测（最稳定） ====================
    js_code = f"""
    <script>
    const username = "{username.strip().replace('"', '\\"')}";
    const password = "{password.strip().replace('"', '\\"')}";
    const servers = {json.dumps(servers)};
    const trans = {json.dumps(trans)};

    // 创建 UI 元素
    let html = `
        <div style="margin:15px 0; padding:15px; border:1px solid #ddd; border-radius:8px; background:#f8f9fa;">
            <h3>${trans.running.replace('{0}', servers.length)}</h3>
            <div id="progressContainer" style="margin:15px 0;">
                <div id="progressBar" style="height:24px; background:#4CAF50; width:0%; border-radius:4px; transition:width 0.3s;"></div>
            </div>
            <div id="progressText" style="text-align:center; font-weight:bold; margin-bottom:10px;">0/{servers.length} (0%)</div>
            <div id="log" style="background:#fff; border:1px solid #eee; padding:12px; height:420px; overflow-y:auto; font-family:monospace; white-space:pre-wrap; font-size:14px;"></div>
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
        const baseUrl = `${server}/player_api.php?username=${username}&password=${password}`;

        const startTime = Date.now();
        logDiv.innerHTML += `${trans.detecting.replace('{0}', index).replace('{1}', servers.length).replace('{2}', server)}\n`;
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
                logDiv.innerHTML += `→ ${trans.http_error.replace('{0}', resp.status).replace('{1}', elapsed)}\n\n`;
            } else {
                const data = await resp.json();
                if (!data || !data.user_info) {
                    logDiv.innerHTML += `→ ${trans.no_userinfo.replace('{0}', elapsed)}\n\n`;
                } else {
                    const ui = data.user_info;
                    let exp = ui.exp_date || "永久";
                    if (/^\\d+$/.test(String(exp))) {
                        exp = new Date(parseInt(exp) * 1000).toLocaleString();
                    }
                    const msg = trans.available.replace('{0}', elapsed)
                                             .replace('{1}', ui.status || "Unknown")
                                             .replace('{2}', exp);
                    logDiv.innerHTML += `→ ${msg}\n\n`;
                }
            }
        } catch (err) {
            const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
            let msg = trans.unknown;
            if (err.name === "AbortError") msg = trans.timeout;
            else if (err.message.includes("CORS") || err.message.includes("fetch")) msg = trans.conn_fail;
            logDiv.innerHTML += `→ ${msg}\n\n`;
        }

        logDiv.scrollTop = logDiv.scrollHeight;
        completed++;

        // 更新进度条
        const percent = Math.round((completed / servers.length) * 100);
        progressBar.style.width = percent + "%";
        progressText.textContent = trans.progress_text.replace('{0}', completed)
                                                       .replace('{1}', servers.length)
                                                       .replace('{2}', percent);
    }

    // 开始检测
    (async () => {
        for (let i = 0; i < servers.length; i++) {
            await testServer(servers[i], i + 1);
            await new Promise(r => setTimeout(r, 400));   // 防止请求过密
        }
        logDiv.innerHTML += `\n${trans.complete.replace('{0}', servers.length)}\n`;
        logDiv.scrollTop = logDiv.scrollHeight;
    })();
    </script>
    """

    st.components.v1.html(js_code, height=650, scrolling=True)

    st.success("✅ 检测已在浏览器中启动！请查看上方实时进度条和日志。")

st.caption(trans["footer"])
st.info("💡 本工具所有检测均从**你的浏览器**发出，更真实。部分服务器因 CORS 会显示失败，属于正常现象。")
