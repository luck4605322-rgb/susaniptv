import streamlit as st
import streamlit.components.v1 as components
import json

# ==================== 1. 页面配置 ====================
st.set_page_config(page_title="IPTV Local Tester", layout="wide", page_icon="📺")

# 多语言简单字典
LANG = {
    "title": "IPTV 访问者本地网络检测工具 v2.0",
    "username": "用户名",
    "password": "密码",
    "servers": "服务器地址 (每行一个)",
    "btn": "🚀 从我的本地网络开始批量检测"
}

# ==================== 2. 主界面布局 ====================
st.title(LANG["title"])
st.markdown("---")

col1, col2 = st.columns([1, 1])
with col1:
    user = st.text_input(LANG["username"])
    pwd = st.text_input(LANG["password"], type="password")
    servers_text = st.text_area(LANG["servers"], height=200, placeholder="example.com:8080")

with col2:
    st.info("""
    **检测原理：**
    - 探测请求由**您的浏览器**直接发出，结果取决于您的本地网络。
    - 自动遵循您的 **Windows 11** 系统代理或 **Clash/Mihomo** 规则。
    """)

# ==================== 3. 核心探测引擎 (修复报错版) ====================
if st.button(LANG["btn"], type="primary", use_container_width=True):
    if not servers_text:
        st.warning("请输入服务器地址")
    else:
        # 处理服务器列表并转换为 JSON 给 JS 使用
        server_list = [s.strip() for s in servers_text.splitlines() if s.strip()]
        js_data = json.dumps(server_list)
        
        # 使用 f-string 注入数据，但通过双大括号 {{ }} 保护 JS 的模板字符串
        components.html(
            f"""
            <div id="box" style="background:#1e1e1e; color:#d4d4d4; padding:20px; font-family:monospace; border-radius:8px; border:1px solid #444;">
                <div id="header" style="color:#569cd6; font-weight:bold; margin-bottom:15px;">📡 正在启动本地网络探测...</div>
                <div id="results" style="max-height:400px; overflow-y:auto;"></div>
            </div>

            <script>
                const servers = {js_data};
                const resultsDiv = document.getElementById('results');
                
                async function check(url) {{
                    const fullUrl = url.startsWith('http') ? url : 'http://' + url;
                    // 使用 no-cors 绕过浏览器跨域限制，仅探测连通性
                    const start = Date.now();
                    try {{
                        await fetch(fullUrl + '/player_api.php', {{ mode: 'no-cors', cache: 'no-cache' }});
                        return {{ status: "✅ 连通", time: Date.now() - start + "ms", color: "#6a9955" }};
                    }} catch (e) {{
                        return {{ status: "❌ 失败", time: "--", color: "#f44747" }};
                    }}
                }}

                async function run() {{
                    for (const s of servers) {{
                        const row = document.createElement('div');
                        row.style.marginBottom = "8px";
                        row.innerHTML = `正在探测: ${{s}} ...`;
                        resultsDiv.appendChild(row);
                        
                        const res = await check(s);
                        row.innerHTML = `<span style="color:${{res.color}}">${{res.status}}</span> | 延迟: ${{res.time}} | 地址: ${{s}}`;
                        resultsDiv.scrollTop = resultsDiv.scrollHeight;
                    }}
                    document.getElementById('header').innerText = "✅ 本地探测任务完成";
                }}

                run();
            </script>
            """,
            height=500
        )
