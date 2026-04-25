import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import json

# ==================== 1. 多国语言字典 ====================
LANGUAGES = {
    "简体中文": {
        "title": "IPTV 客户端本地检测工具 v1.7",
        "username": "用户名", "password": "密码", "servers": "服务器地址（一行一个）",
        "start_btn": "🚀 开始本地批量检测", "result_label": "检测结果 (由您的浏览器执行)",
        "warning": "请填写完整信息！",
        "header_server": "服务器", "header_status": "状态", "header_info": "详细信息",
        "your_ip": "您的公网 IP"
    },
    "English": {
        "title": "IPTV Local Client Tester v1.7",
        "username": "Username", "password": "Password", "servers": "Server Addresses",
        "start_btn": "🚀 Start Local Batch Test", "result_label": "Results (Executed by your browser)",
        "warning": "Please fill in all fields!",
        "header_server": "Server", "header_status": "Status", "header_info": "Details",
        "your_ip": "Your Public IP"
    }
}

# ==================== 2. 页面配置 ====================
st.set_page_config(page_title="IPTV Local Tester", layout="wide", page_icon="📺")

# 侧边栏
st.sidebar.title("Settings / 设定")
lang_choice = st.sidebar.selectbox("Language / 语言", list(LANGUAGES.keys()))
t = LANGUAGES[lang_choice]

st.sidebar.markdown("---")
st.sidebar.subheader(t["your_ip"])

# 1. 浏览器端获取 IP
components.html(
    """
    <div id="ip-display" style="background:#0e1117; color:#ff4b4b; padding:8px; border-radius:5px; border:1px solid #31333f; font-family:monospace; font-size:14px;">检测中...</div>
    <script>
        fetch('https://api.ipify.org?format=json').then(r => r.json())
        .then(d => { document.getElementById('ip-display').innerText = d.ip; })
        .catch(() => { document.getElementById('ip-display').innerText = '未能获取IP'; });
    </script>
    """, height=60
)

# 主界面
st.title(t["title"])
st.info("⚠️ 注意：此工具通过您的浏览器直接请求服务器。如果目标服务器未开启 CORS（跨域资源共享），检测可能会因浏览器安全策略显示 'Fail/CORS Error'。")

col_input, col_info = st.columns([2, 1])

with col_input:
    c1, c2 = st.columns(2)
    with c1:
        user = st.text_input(t["username"])
    with c2:
        pwd = st.text_input(t["password"], type="password")
    servers_text = st.text_area(t["servers"], height=200, placeholder="http://example.com:8080")

# ==================== 3. 核心检测逻辑 (JavaScript 注入) ====================
if st.button(t["start_btn"], type="primary", use_container_width=True):
    if not user or not pwd or not servers_text:
        st.warning(t["warning"])
    else:
        server_list = [s.strip() for s in servers_text.splitlines() if s.strip()]
        
        # 构建传给 JS 的参数
        js_servers = json.dumps(server_list)
        
        # 注入检测脚本
        # 原理：在访问者浏览器中循环 fetch 每个服务器的 player_api.php
        components.html(
            f"""
            <div id="status-box" style="color:#fafafa; font-family:sans-serif; margin-bottom:10px;">正在准备本地检测...</div>
            <div id="results-data" style="display:none;"></div>

            <script>
                const servers = {js_servers};
                const user = "{user}";
                const pass = "{pwd}";
                const results = [];
                const statusBox = document.getElementById('status-box');

                async function checkServers() {{
                    for (let i = 0; i < servers.length; i++) {{
                        let s = servers[i];
                        if (!s.startsWith('http')) s = 'http://' + s;
                        s = s.replace(/\/$/, "");
                        const url = `${{s}}/player_api.php?username=${{user}}&password=${{pass}}`;
                        
                        statusBox.innerText = `检测中 (${{i+1}}/${{servers.length}}): ${{s}}`;
                        
                        const start = Date.now();
                        try {{
                            // 使用 no-cors 模式可以检测是否连通，但无法读取具体 JSON 内容
                            // 如果需要读取具体到期时间，服务器必须允许跨域
                            const response = await fetch(url, {{ mode: 'cors', timeout: 10000 }});
                            const elapsed = ((Date.now() - start)/1000).toFixed(2);
                            
                            if (response.ok) {{
                                results.push({{"Server": s, "Status": "✅ Active", "Details": "Connected in " + elapsed + "s"}});
                            }} else {{
                                results.push({{"Server": s, "Status": "❌ HTTP " + response.status, "Details": "Server unreachable"}});
                            }}
                        }} catch (err) {{
                            results.push({{"Server": s, "Status": "❌ Error", "Details": "Network Error / CORS Block"}});
                        }}
                    }}
                    statusBox.innerHTML = "<b>✅ 本地检测完成！</b> 请查看下方生成的表格。";
                    // 将结果通过文本形式挂载，虽然 Streamlit 获取 JS 变量较难，但这里直接显示在 HTML 组件内
                    document.getElementById('results-data').innerText = JSON.stringify(results);
                    console.table(results);
                </script>
            """,
            height=150,
        )
        
        st.subheader(t["result_label"])
        st.caption("提示：由于浏览器安全限制 (CORS)，如果检测显示 Error，通常是因为目标服务器拒绝了来自此网页的直接请求，但这仍能说明您的本地网络到该服务器的连通性状态。")
