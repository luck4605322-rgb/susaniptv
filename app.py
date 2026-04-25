import streamlit as st
import streamlit.components.v1 as components

html_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>IPTV 本地检测工具</title>
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
            min-height: 350px; 
            white-space: pre-wrap; 
            font-family: monospace;
            overflow: auto;
        }
    </style>
</head>
<body>
<div class="container">
    <h1>🚀 IPTVNator 批量检测工具 - 本地版</h1>
    <p style="text-align:center; color:#94a3b8;">所有检测在您的浏览器中执行（真实网络）</p>

    <label>用户名:</label>
    <input type="text" id="username" placeholder="输入用户名">

    <label>密码:</label>
    <input type="password" id="password" placeholder="输入密码">

    <label>服务器地址（一行一个）:</label>
    <textarea id="servers" rows="10" placeholder="http://example.com:8080"></textarea>

    <button onclick="startTest()">🚀 开始本地批量检测</button>

    <h3>检测结果（实时）:</h3>
    <pre id="result">点击按钮后这里会出现进度...\n如果没有反应，请按 F12 查看控制台</pre>
</div>

<script>
console.log("✅ JS 脚本已加载 - " + new Date().toLocaleTimeString());

async function testSingleServer(server, username, password) {
    console.log("测试服务器:", server);
    if (!server.startsWith("http")) server = "http://" + server;
    server = server.replace(/\/$/, "");
    const url = server + "/player_api.php?username=" + encodeURIComponent(username) + "&password=" + encodeURIComponent(password);
    
    try {
        const resp = await fetch(url, {
            method: "GET",
            signal: AbortSignal.timeout(15000),
            headers: {"User-Agent": "Mozilla/5.0"}
        });
        if (!resp.ok) return `❌ HTTP ${resp.status}`;
        const data = await resp.json();
        if (!data.user_info) return "❌ 登录失败（无 user_info）";
        return "✅ 可用 | 状态: " + (data.user_info.status || "Unknown");
    } catch (e) {
        console.error(e);
        return e.name === "TimeoutError" ? "❌ 超时 (>15s)" : "❌ 连接失败";
    }
}

async function startTest() {
    console.log("🚀 startTest() 函数被触发！");
    alert("✅ 按钮点击成功！\n\n现在请查看 F12 控制台是否有输出或错误。");
    
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();
    const serversText = document.getElementById("servers").value.trim();
    
    if (!username || !password || !serversText) {
        alert("请填写完整信息！");
        return;
    }
    
    const servers = serversText.split("\n").map(s => s.trim()).filter(s => s);
    const resultDiv = document.getElementById("result");
    
    resultDiv.textContent = `开始检测 ${servers.length} 个服务器...\n\n`;
    
    for (let i = 0; i < servers.length; i++) {
        const server = servers[i];
        resultDiv.textContent += `[${i+1}/${servers.length}] 检测中: ${server}\n`;
        
        const res = await testSingleServer(server, username, password);
        resultDiv.textContent += `→ ${res}\n\n`;
        
        await new Promise(r => setTimeout(r, 500));
    }
    
    resultDiv.textContent += "✅ 检测完成！";
}

console.log("脚本初始化完成，按钮已绑定");
</script>
</body>
</html>
"""

st.set_page_config(page_title="IPTV 本地检测工具", layout="wide", page_icon="🚀")

# 关键修复：增大 height + 启用 scrolling
components.html(html_code, height=1100, scrolling=True)

st.info("🔍 **重要**：点击按钮后请立即按 **F12** → Console 标签，查看是否有 'JS 脚本已加载' 或红色错误，然后把内容告诉我。")
