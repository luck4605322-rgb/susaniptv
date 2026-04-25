import streamlit as st
import streamlit.components.v1 as components

html_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>IPTV 测试工具 - 诊断版</title>
    <style>
        body { font-family: system-ui, sans-serif; background: #0f172a; color: #e2e8f0; padding: 20px; }
        .container { max-width: 1000px; margin: auto; }
        button { 
            width: 100%; 
            padding: 18px; 
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
            min-height: 300px; 
            white-space: pre-wrap; 
            font-family: monospace;
        }
    </style>
</head>
<body>
<div class="container">
    <h1>🚀 IPTVNator 批量检测工具 - 诊断版 v1.7</h1>
    <p style="color:#94a3b8;">如果按钮点击后这里没有任何变化，请按 F12 查看控制台错误</p>

    <label>用户名:</label>
    <input type="text" id="username" placeholder="请输入用户名" style="width:100%; padding:10px; margin-bottom:10px;">

    <label>密码:</label>
    <input type="password" id="password" placeholder="请输入密码" style="width:100%; padding:10px; margin-bottom:10px;">

    <label>服务器地址（一行一个）:</label>
    <textarea id="servers" rows="8" placeholder="http://example.com:8080" style="width:100%; padding:10px;"></textarea>

    <button onclick="startTest()">🚀 开始本地批量检测</button>

    <h3>检测结果（实时）:</h3>
    <pre id="result">等待点击按钮...\n（请按 F12 查看控制台是否有红色错误）</pre>
</div>

<script>
console.log("✅ IPTV 诊断版 JS 已成功加载");

async function testSingleServer(server, username, password) {
    console.log("开始测试:", server);
    if (!server.startsWith("http")) server = "http://" + server;
    server = server.replace(/\/$/, "");
    const url = server + "/player_api.php?username=" + encodeURIComponent(username) + "&password=" + encodeURIComponent(password);
    
    try {
        const resp = await fetch(url, { 
            method: "GET", 
            signal: AbortSignal.timeout(15000),
            headers: { "User-Agent": "Mozilla/5.0" }
        });
        console.log("响应状态:", resp.status);
        return "✅ 测试完成（状态 " + resp.status + "）";
    } catch (e) {
        console.error("请求失败:", e);
        return "❌ 请求失败: " + e.message;
    }
}

async function startTest() {
    console.log("🚀 startTest() 函数被成功触发！");
    alert("✅ 按钮点击已触发！\n\n请查看 F12 控制台是否有其他信息。");
    
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();
    const serversText = document.getElementById("servers").value.trim();
    
    if (!username || !password || !serversText) {
        alert("请填写用户名、密码和服务器！");
        return;
    }
    
    const servers = serversText.split("\n").map(s => s.trim()).filter(s => s);
    const resultDiv = document.getElementById("result");
    
    resultDiv.textContent = "🚀 开始检测 " + servers.length + " 个服务器...\n\n";
    
    for (let i = 0; i < servers.length; i++) {
        const server = servers[i];
        resultDiv.textContent += "[" + (i+1) + "/" + servers.length + "] 检测中: " + server + "\n";
        
        const res = await testSingleServer(server, username, password);
        resultDiv.textContent += "→ " + res + "\n\n";
        
        await new Promise(r => setTimeout(r, 500));
    }
    
    resultDiv.textContent += "✅ 检测流程结束";
    console.log("检测完成");
}

// 确保脚本加载后立即输出
console.log("脚本初始化完成，按钮已绑定 onclick");
</script>
</body>
</html>
"""

st.set_page_config(page_title="IPTV 诊断版", layout="wide")

components.html(html_code, height=950, scrolling=True)

st.info("🔍 **诊断提示**：点击按钮后请立即按 **F12** → Console 标签，复制所有红色/黄色信息发给我。")
