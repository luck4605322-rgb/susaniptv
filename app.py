import streamlit as st
import streamlit.components.v1 as components

# ==================== 多国语言字典 ====================
LANGUAGES = {
    "简体中文": {
        "title": "IPTVNator 批量检测工具 v1.6 - 本地检测版",
        "username": "用户名:",
        "password": "密码:",
        "servers": "服务器地址（一行一个）:",
        "start_btn": "🚀 开始本地批量检测",
        "lang_label": "界面语言 / Language:",
        "result_label": "检测结果（实时）:",
        "footer": "v1.6 本地检测版 • 所有请求在您的浏览器中直接执行 • 更真实、更安全",
        "warning": "请填写服务器列表、账号和密码！",
        "running": "🚀 开始检测 {0} 个服务器...\n\n",
        "detecting": "[{0}/{1}] 检测中: {2}\n",
        "complete": "✅ 批量检测完成！共检测 {0} 个服务器。",
        "http_error": "❌ HTTP错误 {0} | 耗时 {1}s",
        "no_userinfo": "❌ 登录失败（无 user_info） | 耗时 {0}s",
        "timeout": "❌ 超时 (>15s)",
        "conn_fail": "❌ 连接失败 (服务器不可达或被阻挡)",
        "unknown": "❌ 未知错误: {0}",
        "available": "✅ 可用 | 耗时 {0}s | 状态: {1} | 过期: {2}"
    },
    "English": {
        "title": "IPTVNator Batch Tester v1.6 - Client-Side",
        "username": "Username:",
        "password": "Password:",
        "servers": "Server Addresses (one per line):",
        "start_btn": "🚀 Start Local Batch Test",
        "lang_label": "Interface Language:",
        "result_label": "Test Results (Live):",
        "footer": "v1.6 Client-Side Version • All requests run in your browser",
        "warning": "Please fill in servers, username and password!",
        "running": "🚀 Testing {0} servers...\n\n",
        "detecting": "[{0}/{1}] Testing: {2}\n",
        "complete": "✅ Batch test completed! Tested {0} servers.",
        "http_error": "❌ HTTP Error {0} | Time {1}s",
        "no_userinfo": "❌ Login failed (no user_info) | Time {0}s",
        "timeout": "❌ Timeout (>15s)",
        "conn_fail": "❌ Connection failed (unreachable or blocked)",
        "unknown": "❌ Unknown error: {0}",
        "available": "✅ Available | Time {0}s | Status: {1} | Exp: {2}"
    },
    # Español 和 Français 可后续补充，当前使用简体中文和英文已足够
}

# ==================== HTML + JS（已修复模板字符串） ====================
html_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>IPTVNator 批量检测工具 v1.6</title>
    <style>
        body { font-family: system-ui, sans-serif; padding: 20px; background: #0f172a; color: #e2e8f0; }
        .container { max-width: 1100px; margin: 0 auto; }
        h1 { color: #60a5fa; }
        label { display: block; margin: 15px 0 6px; font-weight: 600; }
        input, textarea, select { width: 100%; padding: 12px; border: 1px solid #334155; border-radius: 8px; background: #1e2937; color: #e2e8f0; font-size: 16px; }
        button { padding: 14px 28px; font-size: 18px; background: #3b82f6; color: white; border: none; border-radius: 8px; cursor: pointer; margin: 20px 0; }
        button:hover { background: #2563eb; }
        pre { background: #1e2937; color: #94a3b8; padding: 18px; border-radius: 10px; white-space: pre-wrap; font-family: monospace; min-height: 420px; line-height: 1.5; }
        .success { color: #34d399; }
    </style>
</head>
<body>
<div class="container">
    <h1>🚀 IPTVNator 批量检测工具 v1.6 - 本地检测版</h1>
    
    <label id="lang_label">界面语言 / Language:</label>
    <select id="lang_select" onchange="changeLanguage()">
        <option value="简体中文">简体中文</option>
        <option value="English">English</option>
    </select>

    <label id="username_label">用户名:</label>
    <input type="text" id="username" placeholder="username">

    <label id="password_label">密码:</label>
    <input type="password" id="password" placeholder="password">

    <label id="servers_label">服务器地址（一行一个）:</label>
    <textarea id="servers" rows="9" placeholder="http://example.com:8080"></textarea>

    <button onclick="startTest()">🚀 开始本地批量检测</button>

    <h3 id="result_label">检测结果（实时）:</h3>
    <pre id="result"></pre>

    <p id="footer" style="color:#64748b; font-size:14px; margin-top:30px;"></p>
</div>

<script>
const LANGUAGES = """ + str(LANGUAGES).replace("'", '"') + """;
let currentLang = "简体中文";
let trans = LANGUAGES[currentLang];

function updateUI() {
    document.getElementById("lang_label").textContent = trans.lang_label;
    document.getElementById("username_label").textContent = trans.username;
    document.getElementById("password_label").textContent = trans.password;
    document.getElementById("servers_label").textContent = trans.servers;
    document.querySelector("button").textContent = trans.start_btn;
    document.getElementById("result_label").textContent = trans.result_label;
    document.getElementById("footer").innerHTML = trans.footer;
}

function changeLanguage() {
    currentLang = document.getElementById("lang_select").value;
    trans = LANGUAGES[currentLang] || LANGUAGES["简体中文"];
    updateUI();
}

async function testSingleServer(server, username, password) {
    if (!server.startsWith("http")) server = "http://" + server;
    server = server.replace(/\/$/, "");
    const baseUrl = server + "/player_api.php?username=" + encodeURIComponent(username) + "&password=" + encodeURIComponent(password);
    
    const startTime = Date.now();
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 15000);
        
        const resp = await fetch(baseUrl, {
            method: "GET",
            signal: controller.signal,
            headers: { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" }
        });
        clearTimeout(timeoutId);
        
        const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
        
        if (!resp.ok) {
            return "❌ HTTP错误 " + resp.status + " | 耗时 " + elapsed + "s";
        }
        
        const data = await resp.json();
        if (!data || !data.user_info) {
            return "❌ 登录失败（无 user_info） | 耗时 " + elapsed + "s";
        }
        
        const ui = data.user_info;
        let status = ui.status || "Unknown";
        let exp = ui.exp_date || "永久";
        if (/^\\d+$/.test(String(exp))) {
            const date = new Date(exp * 1000);
            exp = date.toLocaleString(currentLang === "简体中文" ? "zh-CN" : "en-US", { hour12: false });
        }
        
        return "✅ 可用 | 耗时 " + elapsed + "s | 状态: " + status + " | 过期: " + exp;
        
    } catch (err) {
        const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
        if (err.name === "AbortError") return "❌ 超时 (>15s)";
        return "❌ 连接失败 (服务器不可达或被阻挡)";
    }
}

async function startTest() {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();
    const serversText = document.getElementById("servers").value.trim();
    
    if (!username || !password || !serversText) {
        alert(trans.warning);
        return;
    }
    
    const servers = serversText.split("\\n").map(s => s.trim()).filter(Boolean);
    const resultDiv = document.getElementById("result");
    
    resultDiv.textContent = "🚀 开始检测 " + servers.length + " 个服务器...\n\n";
    
    for (let i = 0; i < servers.length; i++) {
        const server = servers[i];
        resultDiv.textContent += "[" + (i+1) + "/" + servers.length + "] 检测中: " + server + "\\n";
        
        const resultStr = await testSingleServer(server, username, password);
        resultDiv.textContent += server + "  →  " + resultStr + "\\n\\n";
        
        await new Promise(r => setTimeout(r, 350));
    }
    
    resultDiv.textContent += "\\n✅ " + trans.complete.replace("{0}", servers.length);
}

// 初始化
updateUI();
</script>
</body>
</html>
"""

# ==================== Streamlit 界面 ====================
st.set_page_config(page_title="IPTVNator 批量检测工具 v1.6", layout="wide", page_icon="🚀")

components.html(html_code, height=950, scrolling=True)

st.caption("💡 所有检测请求均在您的浏览器中执行，不经过服务器，更安全、更真实反映您的网络情况。")
