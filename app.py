import streamlit as st
import streamlit.components.v1 as components
import json

# ==================== 1. 页面配置 ====================
st.set_page_config(page_title="IPTV Local Tester", layout="wide", page_icon="📺")

LANG = {
    "title": "IPTV 访问者本地网络真实探测工具 v2.1",
    "username": "用户名",
    "password": "密码",
    "servers": "服务器地址 (例如: example.com:8080)",
    "btn": "🚀 开始真实本地网络检测"
}

# 主界面
st.title(LANG["title"])
st.markdown("---")

col1, col2 = st.columns([1, 1])
with col1:
    user = st.text_input(LANG["username"])
    pwd = st.text_input(LANG["password"], type="password")
    servers_text = st.text_area(LANG["servers"], height=200)

with col2:
    st.info("""
    **为什么之前的版本可能误报？**
    1. **协议安全**：浏览器会禁止从 `https` 页面请求 `http` 资源。
    2. **防火墙拦截**：部分服务器对空头的探测请求非常敏感。
    3. **CORS 限制**：浏览器保护机制可能拦截了正常的连通反馈。
    
    **本版本优化：**
    - 采用 **Image Ping** + **Fetch** 双重探测模式。
    - 请求直接触发您本地 **Windows 11** 环境的真实网络行为。
    """)

# ==================== 2. 核心探测引擎 ====================
if st.button(LANG["btn"], type="primary", use_container_width=True):
    if not servers_text:
        st.warning("请输入服务器地址")
    else:
        server_list = [s.strip() for s in servers_text.splitlines() if s.strip()]
        js_data = json.dumps(server_list)
        
        components.html(
            f"""
            <div id="box" style="background:#0f1116; color:#d4d4d4; padding:20px; font-family:'Segoe UI', Tahoma, sans-serif; border-radius:10px; border:1px solid #333;">
                <div id="ip-tag" style="color:#00ff00; font-family:monospace; margin-bottom:10px;">正在获取您的本地 IP...</div>
                <div id="header" style="color:#569cd6; font-weight:bold; margin-bottom:15px; border-bottom:1px solid #222; padding-bottom:10px;">📡 正在启动本地真实网络探测（不走服务端中转）</div>
                <div id="console" style="max-height:400px; overflow-y:auto; font-family:monospace; font-size:13px;"></div>
            </div>

            <script>
                const servers = {js_data};
                const consoleBox = document.getElementById('console');
                const ipTag = document.getElementById('ip-tag');

                function log(msg, color="#d4d4d4") {{
                    const div = document.createElement('div');
                    div.style.cssText = `color:${{color}}; margin-bottom:6px; border-left:3px solid ${{color}}; padding-left:10px;`;
                    div.innerHTML = `[${{new Date().toLocaleTimeString()}}] ${{msg}}`;
                    consoleBox.appendChild(div);
                    consoleBox.scrollTop = consoleBox.scrollHeight;
                }}

                // 获取访问者 IP
                fetch('https://api.ipify.org?format=json').then(r => r.json())
                    .then(d => {{ ipTag.innerText = "您的当前公网 IP: " + d.ip; }})
                    .catch(() => {{ ipTag.innerText = "IP 获取失败 (可能正在使用代理)"; }});

                // 核心探测函数
                function probe(target) {{
                    return new Promise((resolve) => {{
                        const start = Date.now();
                        let resolved = false;

                        // 模式 1: Image Ping (绕过大多数跨域限制)
                        const img = new Image();
                        img.onload = img.onerror = () => {{
                            if (!resolved) {{ resolved = true; resolve(Date.now() - start); }}
                        }};
                        img.src = `${{target}}/player_api.php?ping=${{start}}`;

                        // 模式 2: Fetch (针对支持跨域的服务器)
                        fetch(target, {{ mode: 'no-cors' }})
                            .then(() => {{ if (!resolved) {{ resolved = true; resolve(Date.now() - start); }} }})
                            .catch(() => {{ /* 忽略错误，等待 Image 结果 */ }});

                        // 超时处理
                        setTimeout(() => {{
                            if (!resolved) {{ resolved = true; resolve(-1); }}
                        }}, 8000);
                    }});
                }}

                async function run() {{
                    log("开始逐一探测服务器连通性...", "#ce9178");
                    for (const s of servers) {{
                        let url = s.startsWith('http') ? s : 'http://' + s;
                        url = url.replace(/\/$/, "");
                        
                        log(`正在尝试连接: ${{url}}`);
                        const latency = await probe(url);
                        
                        if (latency > 0) {{
                            log(`✅ 连通成功 | 延迟: ${{latency}}ms | 地址: ${{url}}`, "#6a9955");
                        }} else {{
                            log(`❌ 探测失败 | 超时或无法访问 | 地址: ${{url}}`, "#f44747");
                        }}
                    }}
                    log("--- 所有探测任务已完成 ---", "#569cd6");
                }}

                setTimeout(run, 1000);
            </script>
            """,
            height=500
        )
