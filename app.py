import streamlit as st
import streamlit.components.v1 as components

html_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>IPTVNator 批量检测工具 v1.6</title>
    <style>
        body { font-family: system-ui, sans-serif; padding: 20px; background: #0f172a; color: #e2e8f0; margin: 0; }
        .container { max-width: 1100px; margin: 0 auto; padding: 20px; }
        h1 { color: #60a5fa; }
        label { display: block; margin: 15px 0 6px; font-weight: 600; }
        input, textarea, select { width: 100%; padding: 12px; border: 1px solid #334155; border-radius: 8px; background: #1e2937; color: #e2e8f0; font-size: 16px; box-sizing: border-box; }
        button { padding: 14px 28px; font-size: 18px; background: #3b82f6; color: white; border: none; border-radius: 8px; cursor: pointer; margin: 20px 0; width: 100%; }
        button:hover { background: #2563eb; }
        pre { background: #1e2937; color: #94a3b8; padding: 18px; border-radius: 10px; white-space: pre-wrap; font-family: monospace; min-height: 420px; line-height: 1.5; overflow: auto; }
    </style>
</head>
<body>
<div class="container">
    <h1>🚀 IPTVNator 批量检测工具 v1.6 - 本地检测版</h1>
    
    <label>界面语言 / Language:</label>
    <select id="lang_select" onchange="changeLanguage()">
        <option value="简体中文">简体中文</option>
        <option value="English">English</option>
    </select>

    <label>用户名:</label>
    <input type="text" id="username" placeholder="username">

    <label>密码:</label>
    <input type="password" id="password" placeholder="password">

    <label>服务器地址（一行一个）:</label>
    <textarea id="servers" rows="9" placeholder="http://example.com:8080"></textarea>

    <button onclick="startTest()">🚀 开始本地批量检测</button>

    <h3>检测结果（实时）:</h3>
    <pre id="result">点击按钮后这里会显示进度...\n（请按 F12 查看控制台是否有错误）</pre>

    <p style="color:#64748b; font-size:14px; margin-top:30px;">
        v1.6 本地检测版 • 所有请求在您的浏览器中执行
    </p>
</div>

<script>
console.log("=== IPTV 测试工具 JS 已加载 ===");

const LANGUAGES = {
    "简体中文": {
        "warning": "请填写用户名、密码和服务器列表！",
        "running": "🚀 开始检测 ",
        "detecting": "检测中: ",
        "complete": "✅ 批量检测完成！共检测 "
    },
    "English": {
        "warning": "Please fill in username, password and servers!",
        "running": "🚀 Testing ",
        "detecting": "Testing: ",
        "complete": "✅ Batch test completed! Tested "
    }
};

let currentLang = "简体中文";
let trans = LANGUAGES[currentLang];

function changeLanguage() {
    currentLang = document.getElementById("lang_select").value;
    trans = LANGUAGES[currentLang] || LANGUAGES["简体中文"];
    console.log("语言切换为:", currentLang);
}

async function testSingleServer(server, username, password) {
    console.log("正在测试服务器:", server);
    if (!server.startsWith("http")) server = "http://" + server;
    server = server.replace(/\/$/, "");
    const url = server + "/player_api.php?username=" + encodeURIComponent(username) + "&password=" + encodeURIComponent(password);
    
    const startTime = Date.now();
    try {
        const controller = new AbortController();
        setTimeout(() => controller.abort(), 15000);
        
        const resp = await fetch(url, {
            method: "GET",
            signal: controller.signal,
            headers: { "User-Agent": "Mozilla/5.0" }
        });
        
        const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
        console.log("响应状态:", resp.status);
        
        if (!resp.ok) return "❌ HTTP错误 " + resp.status + " | 耗时 " + elapsed + "s";
        
        const data = await resp.json();
        if (!data || !data.user_info) return "❌ 登录失败（无 user_info） | 耗时 " + elapsed + "s";
        
        const ui = data.user_info;
        let exp = ui.exp_date || "永久";
        if (/^\\d+$/.test(String(exp))) {
            exp = new Date(exp * 1000).toLocaleString();
        }
        return "✅ 可用 | 耗时 " + elapsed + "s | 状态: " + (ui.status || "Unknown") + " | 过期: " + exp;
        
    } catch (err) {
        console.error("测试失败:", err);
        if (err.name === "AbortError") return "❌ 超时 (>15s)";
        return "❌ 连接失败或被浏览器阻挡（可能是 CORS） | " + err.message;
    }
}

async function startTest() {
    console.log("=== startTest() 被点击执行 ===");
    
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();
    const serversText = document.getElementById("servers").value.trim();
    
    if (!username || !password || !serversText) {
        alert(trans.warning);
        console.warn("输入不完整");
        return;
    }
    
    const servers = serversText.split("\n").map(s => s.trim()).filter(Boolean);
    const resultDiv = document.getElementById("result");
    
    resultDiv.textContent = trans.running + servers.length + " 个服务器...\n\n";
    console.log("开始检测", servers.length, "个服务器");
    
    for (let i = 0; i < servers.length; i++) {
        const server = servers[i];
        resultDiv.textContent += "[" + (i+1) + "/" + servers.length + "] " + trans.detecting + server + "\n";
        
        const resultStr = await testSingleServer(server, username, password);
        resultDiv.textContent += server + " → " + resultStr + "\n\n";
        
        await new Promise(r => setTimeout(r, 400));
    }
    
    resultDiv.textContent += "\n" + trans.complete + servers.length + " 个服务器。";
    console.log("检测流程结束");
}

console.log("脚本初始化完成，按钮已绑定");
</script>
</body>
</html>
"""

st.set_page_config(page_title="IPTVNator 批量检测工具 v1.6", layout="wide", page_icon="🚀")

components.html(html_code, height=1000, scrolling=True)

st.info("💡 **调试提示**：点击按钮后请按 F12 打开控制台，查看是否有红色错误信息，并截图发给我。")
