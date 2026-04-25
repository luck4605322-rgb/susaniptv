import streamlit as st

# ==================== 完整 HTML + JS 代码 ====================
html_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>IPTVNator 本地检测工具 v1.7</title>
    <style>
        body { 
            font-family: system-ui, sans-serif; 
            background: #0f172a; 
            color: #e2e8f0; 
            padding: 20px; 
            margin: 0;
        }
        .container { max-width: 1000px; margin: 0 auto; }
        h1 { color: #60a5fa; text-align: center; }
        label { display: block; margin: 15px 0 5px; font-weight: bold; }
        input, textarea { 
            width: 100%; 
            padding: 12px; 
            margin-bottom: 15px; 
            border: 1px solid #475569; 
            border-radius: 8px; 
            background: #1e2937; 
            color: white; 
            font-size: 16px;
        }
        button { 
            width: 100%; 
            padding: 16px; 
            font-size: 20px; 
            background: #3b82f6; 
            color: white; 
            border: none; 
            border-radius: 10px; 
            cursor: pointer;
            margin: 20px 0;
        }
        button:hover { background: #2563eb; }
        pre { 
            background: #1e2937; 
            padding: 15px; 
            border-radius: 8px; 
            min-height: 400px; 
            white-space: pre-wrap; 
            font-family: monospace;
            overflow: auto;
        }
    </style>
</head>
<body>
<div class="container">
    <h1>🚀 IPTVNator 批量检测工具 v1.7 - 本地检测版</h1>
    <p style="text-align:center; color:#94a3b8;">所有请求直接在您的浏览器中执行，更真实、更安全</p>

    <label>用户名:</label>
    <input type="text" id="username" placeholder="输入用户名">

    <label>密码:</label>
    <input type="password" id="password" placeholder="输入密码">

    <label>服务器地址（一行一个）:</label>
    <textarea id="servers" rows="10" placeholder="http://example.com:8080\nhttp://test.tv:12345"></textarea>

    <button onclick="startTest()">🚀 开始本地批量检测</button>

    <h3>检测结果（实时）:</h3>
    <pre id="result">点击上方按钮开始检测...\n如果没有反应，请按 F12 查看控制台</pre>
</div>

<script>
console.log("✅ IPTV 本地检测工具 JS 已成功加载");

async function testSingleServer(server, username, password) {
    console.log("正在检测:", server);
    if (!server.startsWith("http")) server = "http://" + server;
    server = server.replace(/\/$/, "");
    const url = server + "/player_api.php?username=" + encodeURIComponent(username) + "&password=" + encodeURIComponent(password);
    
    try {
        const resp = await fetch(url, {
            method: "GET",
            signal: AbortSignal.timeout(15000),
            headers: { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" }
        });
        
        if (!resp.ok) return `❌ HTTP错误 ${resp.status}`;
        
        const data = await resp.json();
        if (!data || !data.user_info) return "❌ 登录失败（无 user_info）";
        
        const ui = data.user_info;
        let exp = ui.exp_date || "永久";
        if (/^\\d+$/.test(String(exp))) {
            exp = new Date(exp * 1000).toLocaleString();
        }
        return `✅ 可用 | 状态: ${ui.status || "Unknown"} | 过期: ${exp}`;
    } catch (e) {
        console.error(e);
        return e.name === "TimeoutError" ? "❌ 超时 (>15s)" : "❌ 连接失败或被阻挡";
    }
}

async function startTest() {
    console.log("🚀 startTest() 被成功触发！");
    
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();
    const serversText = document.getElementById("servers").value.trim();
    
    if (!username || !password || !serversText) {
        alert("请填写用户名、密码和服务器列表！");
        return;
    }
    
    const servers = serversText.split("\n").map(s => s.trim()).filter(s => s);
    const resultDiv = document.getElementById("result");
    
    resultDiv.textContent = `🚀 开始检测 ${servers.length} 个服务器...\n\n`;
    
    for (let i = 0; i < servers.length; i++) {
        const server = servers[i];
        resultDiv.textContent += `[${i+1}/${servers.length}] 检测中: ${server}\n`;
        
        const res = await testSingleServer(server, username, password);
        resultDiv.textContent += `→ ${res}\n\n`;
        
        await new Promise(r => setTimeout(r, 400));
    }
    
    resultDiv.textContent += "✅ 批量检测完成！";
    console.log("检测流程结束");
}
</script>
</body>
</html>
"""

st.set_page_config(page_title="IPTVNator 本地检测工具", layout="wide", page_icon="🚀")

# 使用 st.html + unsafe_allow_javascript=True（关键修复）
st.html(html_code, unsafe_allow_javascript=True)

st.caption("💡 本工具所有网络请求均在您的浏览器本地执行，不会经过任何服务器。")
st.info("🔍 点击按钮后若无反应，请按 **F12** → Console 查看是否有错误信息，并告诉我。")
