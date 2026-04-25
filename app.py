import streamlit as st
import time

# ==================== 1. 多国语言字典（保持原样，略有精简标题） ====================
LANGUAGES = {
    "简体中文": {
        "title": "IPTVNator 网页批量检测工具 v2.0（客户端检测）--作者 susan",
        "username": "用户名", "password": "密码", "servers": "服务器地址（一行一个）",
        "start_btn": "🚀 开始批量检测", "result_label": "检测结果", "warning": "请填写完整信息！",
        "header_server": "服务器", "header_status": "状态", "header_info": "详细信息",
        "your_ip": "您的公网 IP（客户端）", "testing": "正在测试...", "done": "检测完成！"
    },
    "English": {
        "title": "IPTVNator Web Tester v2.0 (Client-side) -- Author susan",
        "username": "Username", "password": "Password", "servers": "Server Addresses (one per line)",
        "start_btn": "🚀 Start Batch Test", "result_label": "Test Results", "warning": "Please fill in all fields!",
        "header_server": "Server", "header_status": "Status", "header_info": "Details",
        "your_ip": "Your Public IP (Client)", "testing": "Testing...", "done": "Test Completed!"
    },
    # 其他语言可按需补充，保持一致结构
    "日本語": { ... },  # 你可以复制原字典补充
    "한국어": { ... },
    "Español": { ... },
    "Français": { ... },
    "Deutsch": { ... },
}

# ==================== 2. Streamlit 页面布局 ====================
st.set_page_config(page_title="IPTV Batch Tester", layout="wide", page_icon="📺")

lang_choice = st.sidebar.selectbox("Language / 语言", list(LANGUAGES.keys()))
t = LANGUAGES[lang_choice]

st.title(t["title"])
st.markdown("---")

# 客户端公网 IP（通过 JS 获取）
st.sidebar.title("Settings")
st.sidebar.subheader(t["your_ip"])
ip_placeholder = st.sidebar.empty()

col_input, col_info = st.columns([2, 1])

with col_input:
    c1, c2 = st.columns(2)
    with c1:
        user = st.text_input(t["username"])
    with c2:
        pwd = st.text_input(t["password"], type="password")
    
    servers_text = st.text_area(t["servers"], height=250, 
                                placeholder="http://example.com:8080\nhttp://another-server.net")

with col_info:
    st.info(f"""
    **重要提示：**
    - 检测现在**从您的浏览器直接发起**（使用您的本地网络）
    - 支持多线程并行测试（浏览器限制约 6-10 个并发）
    - 部分服务器可能因 CORS 策略无法返回详细 JSON，仅显示是否可达
    - 推荐使用 Chrome/Firefox 浏览器
    """)

# ==================== 3. 客户端 JS 检测脚本 ====================
if st.button(t["start_btn"], type="primary", use_container_width=True):
    if not user or not pwd or not servers_text.strip():
        st.warning(t["warning"])
    else:
        servers = [s.strip() for s in servers_text.splitlines() if s.strip()]
        if not servers:
            st.warning("请输入至少一个服务器地址！")
            st.stop()

        # 显示加载状态
        progress_bar = st.progress(0)
        status_msg = st.empty()
        result_placeholder = st.empty()

        # 生成客户端检测的完整 HTML + JS
        html_code = f"""
        <div id="results"></div>
        <script>
        const username = "{user}";
        const password = "{pwd}";
        const servers = {servers};
        const total = servers.length;
        let completed = 0;
        const results = [];

        async function testServer(server) {{
            if (!server.startsWith("http")) server = "http://" + server;
            server = server.replace(/\\/$/, "");
            const baseUrl = `${{server}}/player_api.php?username=${{username}}&password=${{password}}`;
            const startTime = Date.now();

            try {{
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 12000);

                const response = await fetch(baseUrl, {{
                    method: 'GET',
                    headers: {{ "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" }},
                    signal: controller.signal,
                    mode: 'no-cors'   // 处理大多数 IPTV 服务器的 CORS 限制
                }});

                clearTimeout(timeoutId);
                const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);

                let status = "✅ Reachable";
                let details = `Time: ${{elapsed}}s (CORS limited - status unknown)`;

                // 如果 no-cors 仍然能得到 response.type === 'opaque'，我们无法读取内容
                // 但至少能判断网络可达 + 响应时间

                results.push({{
                    Server: server,
                    Status: status,
                    Details: details
                }});

            }} catch (err) {{
                const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
                let statusText = "❌ Unreachable";
                if (err.name === 'AbortError') statusText = "❌ Timeout";

                results.push({{
                    Server: server,
                    Status: statusText,
                    Details: `Error: ${{err.message || 'Network issue'}} | ${{elapsed}}s`
                }});
            }}

            completed++;
            const prog = Math.round((completed / total) * 100);
            
            // 更新进度（通过 window.parent 向 Streamlit 通信较复杂，这里用简单 console + 最终渲染）
            console.log(`Progress: ${{prog}}%`);

            // 每完成一个就渲染一次结果（实时更新）
            renderResults();
        }}

        function renderResults() {{
            let html = `
                <table style="width:100%; border-collapse: collapse; margin-top: 20px;">
                    <thead>
                        <tr style="background:#f0f2f6;">
                            <th style="padding:12px; text-align:left; border:1px solid #ddd;">{t["header_server"]}</th>
                            <th style="padding:12px; text-align:left; border:1px solid #ddd;">{t["header_status"]}</th>
                            <th style="padding:12px; text-align:left; border:1px solid #ddd;">{t["header_info"]}</th>
                        </tr>
                    </thead>
                    <tbody>`;
            
            results.forEach(r => {{
                const statusColor = r.Status.includes("✅") ? "green" : "red";
                html += `
                    <tr>
                        <td style="padding:10px; border:1px solid #ddd;">${{r.Server}}</td>
                        <td style="padding:10px; border:1px solid #ddd; color:${{statusColor}};">${{r.Status}}</td>
                        <td style="padding:10px; border:1px solid #ddd;">${{r.Details}}</td>
                    </tr>`;
            }});
            
            html += `</tbody></table>`;
            document.getElementById("results").innerHTML = html;
        }}

        // 并行执行（浏览器会自动限制并发）
        Promise.all(servers.map(s => testServer(s))).then(() => {{
            console.log("{t['done']}");
        }});

        // 初始渲染空表
        renderResults();
        </script>
        """

        # 在 Streamlit 中渲染客户端 JS
        with result_placeholder:
            st.subheader(t["result_label"])
            st.components.v1.html(html_code, height=600, scrolling=True)

        st.success(t["done"])

# ==================== 客户端 IP 获取（可选增强） ====================
# 在页面加载时通过 JS 获取客户端 IP 并显示在侧边栏
ip_js = """
<script>
fetch('https://api.ipify.org?format=json')
  .then(r => r.json())
  .then(data => {
    const ipEl = document.querySelector('#client-ip');
    if (ipEl) ipEl.textContent = data.ip;
  })
  .catch(() => {});
</script>
<div id="client-ip" style="font-family: monospace; background:#f0f2f6; padding:8px; border-radius:4px;"></div>
"""

ip_placeholder.markdown("**Detected:**")
st.components.v1.html(ip_js, height=60)

st.caption("注意：检测完全在您的浏览器中执行，使用您的本地网络。GitHub 服务器仅提供页面。")
