import streamlit as st
import requests
import time

# ==================== 多国语言字典（完整版） ====================
LANGUAGES = {
    "简体中文": {
        "title": "IPTVNator 批量检测工具 v1.5 - 简易可用性检测",
        "username": "用户名:",
        "password": "密码:",
        "servers": "服务器地址（一行一个）:",
        "example": "填入示例",
        "start_btn": "🚀 开始批量检测",
        "lang_label": "界面语言 / Language:",
        "result_label": "检测结果（实时）:",
        "footer": "v1.5 简易版 • 只检测是否可用 + 状态 + 过期时间 • Streamlit版",
        "warning": "请填写服务器列表、账号和密码！",
        "running": "🚀 开始检测 {0} 个服务器...",
        "only_first": "",
        "single": "",
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
        "title": "IPTVNator Batch Tester v1.5 - Simple Availability Check",
        "username": "Username:",
        "password": "Password:",
        "servers": "Server Addresses (one per line):",
        "example": "Load Example",
        "start_btn": "🚀 Start Batch Test",
        "lang_label": "Interface Language:",
        "result_label": "Test Results (Live):",
        "footer": "v1.5 Simple Version • Only checks availability + status + expiration • Streamlit",
        "warning": "Please fill in servers, username and password!",
        "running": "🚀 Testing {0} servers...",
        "only_first": "",
        "single": "",
        "detecting": "[{0}/{1}] Testing: {2}\n",
        "complete": "✅ Batch test completed! Tested {0} servers.",
        "http_error": "❌ HTTP Error {0} | Time {1}s",
        "no_userinfo": "❌ Login failed (no user_info) | Time {0}s",
        "timeout": "❌ Timeout (>15s)",
        "conn_fail": "❌ Connection failed (unreachable or blocked)",
        "unknown": "❌ Unknown error: {0}",
        "available": "✅ Available | Time {0}s | Status: {1} | Exp: {2}"
    },
    "Español": {
        "title": "Herramienta de Prueba IPTVNator v1.5 - Comprobación Simple",
        "username": "Usuario:",
        "password": "Contraseña:",
        "servers": "Direcciones del servidor (una por línea):",
        "example": "Cargar ejemplo",
        "start_btn": "🚀 Iniciar prueba por lotes",
        "lang_label": "Idioma de la interfaz:",
        "result_label": "Resultados de la prueba (en vivo):",
        "footer": "v1.5 Versión Simple • Solo verifica disponibilidad + estado + expiración",
        "warning": "¡Por favor complete servidores, usuario y contraseña!",
        "running": "🚀 Probando {0} servidores...",
        "only_first": "",
        "single": "",
        "detecting": "[{0}/{1}] Probando: {2}\n",
        "complete": "✅ ¡Prueba por lotes completada! Se probaron {0} servidores.",
        "http_error": "❌ Error HTTP {0} | Tiempo {1}s",
        "no_userinfo": "❌ Fallo de inicio de sesión (sin user_info) | Tiempo {0}s",
        "timeout": "❌ Tiempo de espera agotado (>15s)",
        "conn_fail": "❌ Fallo de conexión (servidor inaccesible o bloqueado)",
        "unknown": "❌ Error desconocido: {0}",
        "available": "✅ Disponible | Tiempo {0}s | Estado: {1} | Expira: {2}"
    },
    "Français": {
        "title": "Outil de Test IPTVNator v1.5 - Vérification Simple",
        "username": "Nom d'utilisateur:",
        "password": "Mot de passe:",
        "servers": "Adresses du serveur (une par ligne):",
        "example": "Charger exemple",
        "start_btn": "🚀 Lancer le test par lots",
        "lang_label": "Langue de l'interface:",
        "result_label": "Résultats du test (temps réel):",
        "footer": "v1.5 Version Simple • Vérifie uniquement la disponibilité + statut + expiration",
        "warning": "Veuillez remplir les serveurs, nom d'utilisateur et mot de passe !",
        "running": "🚀 Test de {0} serveurs...",
        "only_first": "",
        "single": "",
        "detecting": "[{0}/{1}] Test en cours: {2}\n",
        "complete": "✅ Test par lots terminé ! {0} serveurs testés.",
        "http_error": "❌ Erreur HTTP {0} | Temps {1}s",
        "no_userinfo": "❌ Échec de connexion (pas de user_info) | Temps {0}s",
        "timeout": "❌ Délai dépassé (>15s)",
        "conn_fail": "❌ Échec de connexion (serveur inaccessible ou bloqué)",
        "unknown": "❌ Erreur inconnue: {0}",
        "available": "✅ Disponible | Temps {0}s | Statut: {1} | Expiration: {2}"
    }
}

# ==================== 请求头 ====================
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "close",
    "Cache-Control": "no-cache",
}

def test_single_server(server, username, password, trans):
    if not server.startswith("http"):
        server = "http://" + server
    server = server.rstrip("/")
    base_url = f"{server}/player_api.php?username={username}&password={password}"
    
    start_time = time.time()
    session = requests.Session()
    
    try:
        resp = session.get(base_url, headers=HEADERS, timeout=15, allow_redirects=True)
        elapsed = round(time.time() - start_time, 2)
        
        if resp.status_code != 200:
            result = trans["http_error"].format(resp.status_code, elapsed)
            return f"{server}  →  {result}", False
        
        data = resp.json()
        if not (isinstance(data, dict) and "user_info" in data):
            result = trans["no_userinfo"].format(elapsed)
            return f"{server}  →  {result}", False
        
        ui = data.get("user_info", {})
        status = ui.get("status", "Unknown")
        exp = ui.get("exp_date", "永久")
        if str(exp).isdigit():
            exp = time.strftime("%Y-%m-%d %H:%M", time.localtime(int(exp)))
        
        result = trans["available"].format(elapsed, status, exp)
        return f"{server}  →  {result}", True
        
    except requests.exceptions.Timeout:
        result = trans["timeout"]
    except requests.exceptions.ConnectionError:
        result = trans["conn_fail"]
    except Exception as e:
        result = trans["unknown"].format(str(e)[:80])
    
    return f"{server}  →  {result}", False

# ==================== Streamlit 界面 ====================
st.set_page_config(page_title="IPTVNator 批量检测工具 v1.5", layout="wide", page_icon="🚀")
st.title("🚀 IPTVNator 批量检测工具 v1.5 - 简易可用性检测")

# 语言切换
lang = st.selectbox(LANGUAGES["简体中文"]["lang_label"], options=list(LANGUAGES.keys()), index=0)
trans = LANGUAGES[lang]

col1, col2 = st.columns([2, 1])
with col1:
    username = st.text_input(trans["username"], placeholder="username")
    password = st.text_input(trans["password"], type="password", placeholder="password")
with col2:
    if st.button(trans["example"], use_container_width=True):
        st.session_state["servers"] = "http://example.com:8080\nhttp://test.tv:12345\nhttp://backup.server:9999"

servers_input = st.text_area(
    trans["servers"],
    height=200,
    value=st.session_state.get("servers", ""),
    placeholder="一行一个服务器地址\nhttp://example.com:8080"
)

if st.button(trans["start_btn"], type="primary", use_container_width=True):
    servers = [s.strip() for s in servers_input.strip().splitlines() if s.strip()]
    username_str = username.strip()
    password_str = password.strip()

    if not servers or not username_str or not password_str:
        st.error(trans["warning"])
        st.stop()

    result_text = trans["running"].format(len(servers)) + "\n\n"
    
    result_placeholder = st.empty()
    result_placeholder.markdown(result_text)

    for i, server in enumerate(servers, 1):
        result_text += trans["detecting"].format(i, len(servers), server)
        result_placeholder.markdown(result_text)

        result_str, _ = test_single_server(server, username_str, password_str, trans)
        
        result_text += result_str + "\n\n"
        result_placeholder.markdown(result_text)

        time.sleep(0.3)

    result_text += "\n" + trans["complete"].format(len(servers))
    result_placeholder.markdown(result_text)
    st.success("✅ 检测完成！")

st.caption(trans["footer"])
st.markdown("---")
st.info("💡 本版本仅检测登录是否成功，不再统计直播/电影数量，速度更快。")
