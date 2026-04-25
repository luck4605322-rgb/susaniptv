import streamlit as st
import streamlit.components.v1 as components
import json

# ==================== 1. 页面配置与多国语言 ====================
st.set_page_config(page_title="IPTV Local Tester", layout="wide", page_icon="📺")

LANGUAGES = {
    "简体中文": {
        "title": "IPTV 客户端本地检测工具 v1.9",
        "username": "用户名", "password": "密码",
        "servers": "服务器地址（一行一个，不带 http://）",
        "start_btn": "🚀 开始本地真实网络检测",
        "your_ip": "您的访问 IP"
    },
    "English": {
        "title": "IPTV Local Network Tester v1.9",
        "username": "Username", "password": "Password",
        "servers": "Servers (one per line, without http://)",
        "start_btn": "🚀 Start Local Test",
        "your_ip": "Your IP"
    }
}

# 侧边栏
st.sidebar.title("Settings / 设定")
lang_choice = st.sidebar.selectbox("Language / 语言", list(LANGUAGES.keys()))
t = LANGUAGES[lang_choice]

# ==================== 2. 主界面布局 ====================
st.title(t["title"])
st.markdown("---")

col_input, col_info = st.columns([1, 1])

with col_input:
    user = st.text_input(t["username"], key="user")
    pwd = st.text_input(t["password"], type="password", key="pass")
    servers_text = st.text_area(t["servers"], height=200, placeholder="example.com:8080")

with col_info:
    st.info("""
    **运行说明：**
    1. 探测请求由您的**浏览器直接发出**，反映您当前的真实网络。
    2. 检测结果会经过您的 **Windows 11** 系统代理（如 **Clash Verge Rev** 或 **Mihomo Party**）。
    3. 如果在 **1Panel** 环境下部署，请确保容器映射了正确的端口。
    """)

# ==================== 3. 核心探测组件 (JavaScript) ====================
if st.button(t["start_btn"], type="primary", use_container_width=True):
    if not servers_text:
        st.warning("请先输入服务器地址！")
    else:
        # 处理服务器列表
        server_list = [s.strip() for s in servers_text.splitlines() if s.strip()]
        js_servers = json.dumps(server_list)
        
        # 注入 HTML/JS 组件
        components.html(
            f"""
            <div id="root" style="background:#1e1e1e; color:#d4d4d4; padding:20px; font-family:Consolas, monospace; border-radius:10px; border:1px solid #333;">
                <div id="ip-header" style="color:#569cd6; margin-bottom:15px; border-bottom:1px solid #444; padding-bottom:10px;">
                    正在获取本地公网 IP...
                </div>
                <div id="console" style="height:300px; overflow-y:auto; font-size:13px; line-height:1.6;">
                    > 等待指令...
                </div>
            </div>

            <script>
                const servers = {js_servers};
                const consoleBox = document.getElementById('console');
                const ipHeader = document.getElementById('ip-header');

                function log(msg, color="#d4d4d4") {{
                    const div = document.createElement('div');
                    div.style.color = color;
                    div.innerHTML = `[${{new Date().toLocaleTimeString()}}] ${{msg}}`;
                    consoleBox.appendChild(div);
                    consoleBox.scrollTop = consoleBox.scrollHeight;
                }}

                // 1. 获取真实公网 IP
                fetch('https://api.ipify.org?format=json')
                    .then(r => r.json())
                    .then(d => {{ ipHeader.innerText = "您的当前出口 IP: " + d.ip; }})
                    .catch(() => {{ ipHeader.innerText = "IP 获取失败 (请检查代理规则)"; }});

                // 2. 探测函数 (使用 fetch no-cors 模式绕过安全限制)
                async function check(url) {{
                    const fullUrl = url.startsWith('http') ? url : 'http://' + url;
                    const target = `${{fullUrl}}/player_api.php`;
                    const start = Date.now();
                    
                    try {{
                        // no-cors 允许浏览器发出请求并接收“不透明”响应，足以判断网络连通性
                        await fetch(target, {{ mode: 'no-cors', cache: 'no-cache' }});
                        const duration = Date.now() - start;
                        return {{ success: true, time: duration }};
                    }} catch (e) {{
                        return {{ success: false, time: Date.now() - start }};
                    }}
                }}

                async function startTask() {{
                    log("开始检测本地网络到目标服务器的连通性...", "#ce9178");
                    for (const s of servers) {{
                        log(`正在探测: ${{s}}`);
                        const result = await check(s);
                        if (result.success) {{
                            log(`✅ 连通成功 | 响应延迟: ${{result.time}}ms`, "#6a9955");
                        }} else {{
                            log(`❌ 无法访问 | 请检查该地址或您的代理分流`, "#f44747");
                        }}
                    }}
                    log("检测任务结束。", "#569cd6");
                }}

                setTimeout(startTask, 500);
            </script>
            """,
            height=500,
        )
