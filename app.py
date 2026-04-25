import flet as ft
import requests
import threading
import time
from collections import defaultdict

# ==================== 多国语言字典（完整版） ====================
LANGUAGES = {
    "简体中文": {
        "title": "IPTVNator 批量检测工具 v1.5 (Web版)",
        "username": "用户名:",
        "password": "密码:",
        "servers": "服务器地址（一行一个）:",
        "example": "填入示例",
        "start_btn": "🚀 开始批量检测",
        "lang_label": "界面语言 / Language:",
        "result_label": "检测结果（实时）:",
        "footer": "v1.5 Web版 • Flet 构建 • 仅第一个成功服务器检测直播/电影/语言分类 • 基于 Xtream API",
        "warning": "请填写服务器列表、账号和密码！",
        "running": "🚀 开始检测 {0} 个服务器...",
        "only_first": "   → 只对第一个成功登录的服务器检测直播数量、电影数量和多国语言分类\n\n",
        "single": "   → 将检测直播数量、电影数量和常用多国语言分类\n\n",
        "detecting": "[{0}/{1}] 检测中: {2}\n",
        "complete": "✅ 批量检测完成！共检测 {0} 个服务器。",
        "http_error": "❌ HTTP错误 {0} | 耗时 {1}s",
        "no_userinfo": "❌ 登录失败（无 user_info） | 耗时 {0}s",
        "timeout": "❌ 超时 (>15s)",
        "conn_fail": "❌ 连接失败 (服务器不可达或被阻挡)",
        "unknown": "❌ 未知错误: {0}",
        "available": "✅ 可用 | 耗时 {0}s | 状态: {1} | 过期: {2} | 直播: {3}个 | 电影: {4}个{5}",
        "no_resource": "✅ 可用 | 耗时 {0}s | 状态: {1} | 过期: {2} | （资源&语言已检测过其他服务器）",
        "lang_stats": " | 语言分类: {0}"
    },
    "English": {
        "title": "IPTVNator Batch Tester v1.5 (Web)",
        "username": "Username:",
        "password": "Password:",
        "servers": "Server Addresses (one per line):",
        "example": "Load Example",
        "start_btn": "🚀 Start Batch Test",
        "lang_label": "Interface Language:",
        "result_label": "Test Results (Live):",
        "footer": "v1.5 Web Version • Built with Flet • Only first successful server checks Live/Movies/Languages",
        "warning": "Please fill in servers, username and password!",
        "running": "🚀 Testing {0} servers...",
        "only_first": "   → Only the first successful server will check live count, movie count and language categories\n\n",
        "single": "   → Will check live count, movie count and common language categories\n\n",
        "detecting": "[{0}/{1}] Testing: {2}\n",
        "complete": "✅ Batch test completed! Tested {0} servers.",
        "http_error": "❌ HTTP Error {0} | Time {1}s",
        "no_userinfo": "❌ Login failed (no user_info) | Time {0}s",
        "timeout": "❌ Timeout (>15s)",
        "conn_fail": "❌ Connection failed (unreachable or blocked)",
        "unknown": "❌ Unknown error: {0}",
        "available": "✅ Available | Time {0}s | Status: {1} | Exp: {2} | Live: {3} | Movies: {4}{5}",
        "no_resource": "✅ Available | Time {0}s | Status: {1} | Exp: {2} | (Resources & languages checked on another server)",
        "lang_stats": " | Languages: {0}"
    },
    "Español": {
        "title": "Herramienta de Prueba IPTVNator v1.5 (Web)",
        "username": "Usuario:",
        "password": "Contraseña:",
        "servers": "Direcciones del servidor (una por línea):",
        "example": "Cargar ejemplo",
        "start_btn": "🚀 Iniciar prueba por lotes",
        "lang_label": "Idioma de la interfaz:",
        "result_label": "Resultados de la prueba (en vivo):",
        "footer": "v1.5 Versión Web • Solo el primer servidor exitoso verifica canales/películas/idiomas",
        "warning": "¡Por favor complete servidores, usuario y contraseña!",
        "running": "🚀 Probando {0} servidores...",
        "only_first": "   → Solo el primer servidor exitoso verificará cantidad de canales, películas y categorías de idioma\n\n",
        "single": "   → Se verificarán cantidad de canales, películas y categorías de idioma\n\n",
        "detecting": "[{0}/{1}] Probando: {2}\n",
        "complete": "✅ ¡Prueba por lotes completada! Se probaron {0} servidores.",
        "http_error": "❌ Error HTTP {0} | Tiempo {1}s",
        "no_userinfo": "❌ Fallo de inicio de sesión (sin user_info) | Tiempo {0}s",
        "timeout": "❌ Tiempo de espera agotado (>15s)",
        "conn_fail": "❌ Fallo de conexión (servidor inaccesible o bloqueado)",
        "unknown": "❌ Error desconocido: {0}",
        "available": "✅ Disponible | Tiempo {0}s | Estado: {1} | Expira: {2} | Canales: {3} | Películas: {4}{5}",
        "no_resource": "✅ Disponible | Tiempo {0}s | Estado: {1} | Expira: {2} | (Recursos verificados en otro servidor)",
        "lang_stats": " | Idiomas: {0}"
    },
    "Français": {
        "title": "Outil de Test par Lots IPTVNator v1.5 (Web)",
        "username": "Nom d'utilisateur:",
        "password": "Mot de passe:",
        "servers": "Adresses du serveur (une par ligne):",
        "example": "Charger exemple",
        "start_btn": "🚀 Lancer le test par lots",
        "lang_label": "Langue de l'interface:",
        "result_label": "Résultats du test (temps réel):",
        "footer": "v1.5 Version Web • Seul le premier serveur réussi vérifie live/films/langues",
        "warning": "Veuillez remplir les serveurs, nom d'utilisateur et mot de passe !",
        "running": "🚀 Test de {0} serveurs...",
        "only_first": "   → Seul le premier serveur réussi vérifiera le nombre de chaînes, films et catégories de langue\n\n",
        "single": "   → Vérifiera le nombre de chaînes, films et catégories de langue\n\n",
        "detecting": "[{0}/{1}] Test en cours: {2}\n",
        "complete": "✅ Test par lots terminé ! {0} serveurs testés.",
        "http_error": "❌ Erreur HTTP {0} | Temps {1}s",
        "no_userinfo": "❌ Échec de connexion (pas de user_info) | Temps {0}s",
        "timeout": "❌ Délai dépassé (>15s)",
        "conn_fail": "❌ Échec de connexion (serveur inaccessible ou bloqué)",
        "unknown": "❌ Erreur inconnue: {0}",
        "available": "✅ Disponible | Temps {0}s | Statut: {1} | Expiration: {2} | Live: {3} | Films: {4}{5}",
        "no_resource": "✅ Disponible | Temps {0}s | Statut: {1} | Expiration: {2} | (Ressources vérifiées sur un autre serveur)",
        "lang_stats": " | Langues: {0}"
    }
}

# ==================== 请求头（防封锁） ====================
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "close",
    "Cache-Control": "no-cache",
}

# ==================== 语言分类映射 ====================
LANGUAGE_MAP = {
    "english": "English", "eng": "English",
    "arabic": "Arabic", "ara": "Arabic",
    "chinese": "Chinese", "china": "Chinese", "中文": "Chinese",
    "spanish": "Spanish", "esp": "Spanish",
    "french": "French", "fra": "French",
    "german": "German", "deu": "German",
    "italian": "Italian", "ita": "Italian",
    "russian": "Russian", "rus": "Russian",
    "turkish": "Turkish", "tur": "Turkish",
    "portuguese": "Portuguese", "por": "Portuguese",
    "hindi": "Hindi/India", "india": "Hindi/India",
    "korean": "Korean", "kor": "Korean",
    "japanese": "Japanese", "jpn": "Japanese",
}

def get_language_stats(categories):
    lang_count = defaultdict(int)
    for cat in categories:
        if not isinstance(cat, dict):
            continue
        name = str(cat.get("category_name", "")).lower()
        matched = False
        for key, lang in LANGUAGE_MAP.items():
            if key in name:
                lang_count[lang] += 1
                matched = True
                break
        if not matched and any(w in name for w in ["international", "world", "global", "sport", "news"]):
            lang_count["International"] += 1
    return dict(lang_count)

def get_resource_counts(session, base_url):
    live_count = vod_count = 0
    try:
        r = session.get(f"{base_url}&action=get_live_streams", headers=HEADERS, timeout=12)
        if r.status_code == 200 and isinstance(r.json(), list):
            live_count = len(r.json())
    except:
        pass
    try:
        r = session.get(f"{base_url}&action=get_vod_streams", headers=HEADERS, timeout=12)
        if r.status_code == 200 and isinstance(r.json(), list):
            vod_count = len(r.json())
    except:
        pass
    return live_count, vod_count

def get_language_categories(session, base_url):
    try:
        r = session.get(f"{base_url}&action=get_live_categories", headers=HEADERS, timeout=10)
        if r.status_code == 200:
            cats = r.json()
            if isinstance(cats, list):
                return get_language_stats(cats)
    except:
        pass
    return {}

def test_single_server(server, username, password, trans, check_resources=True):
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
        
        lang_info = ""
        if check_resources:
            live_c, vod_c = get_resource_counts(session, base_url)
            lang_stats = get_language_categories(session, base_url)
            if lang_stats:
                parts = [f"{k}({v})" for k, v in sorted(lang_stats.items(), key=lambda x: -x[1])]
                lang_info = trans["lang_stats"].format(", ".join(parts[:8]))
            result = trans["available"].format(elapsed, status, exp, live_c, vod_c, lang_info)
        else:
            result = trans["no_resource"].format(elapsed, status, exp)
        
        return f"{server}  →  {result}", True
        
    except requests.exceptions.Timeout:
        result = trans["timeout"]
    except requests.exceptions.ConnectionError:
        result = trans["conn_fail"]
    except Exception as e:
        result = trans["unknown"].format(str(e)[:80])
    
    return f"{server}  →  {result}", False

# ==================== Flet 主应用 ====================
def main(page: ft.Page):
    page.title = "IPTVNator 批量检测工具 v1.5 (Web)"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = "auto"
    page.window_min_width = 1100
    page.window_min_height = 750

    current_lang = "简体中文"
    trans = LANGUAGES[current_lang]

    title = ft.Text(trans["title"], size=28, weight="bold", color=ft.colors.BLUE_400)

    lang_dropdown = ft.Dropdown(
        label=trans["lang_label"],
        options=[ft.dropdown.Option(lang) for lang in LANGUAGES.keys()],
        value=current_lang,
        width=250,
    )

    username_field = ft.TextField(label=trans["username"], width=650, dense=True)
    password_field = ft.TextField(label=trans["password"], password=True, can_reveal_password=True, width=650, dense=True)
    
    servers_field = ft.TextField(
        label=trans["servers"],
        multiline=True,
        min_lines=12,
        max_lines=18,
        width=850,
        hint_text="http://example.com:8080\nhttp://test.tv:12345\nhttp://backup.server:9999",
    )

    result_area = ft.TextField(
        value="",
        multiline=True,
        read_only=True,
        min_lines=22,
        max_lines=35,
        width=1100,
        text_size=13,
        font_family="Consolas",
    )

    progress_ring = ft.ProgressRing(visible=False, width=32, height=32, stroke_width=4)

    def change_language(e):
        nonlocal trans, current_lang
        new_lang = lang_dropdown.value
        if new_lang == current_lang:
            return
        current_lang = new_lang
        trans = LANGUAGES[new_lang]
        title.value = trans["title"]
        lang_dropdown.label = trans["lang_label"]
        username_field.label = trans["username"]
        password_field.label = trans["password"]
        servers_field.label = trans["servers"]
        start_btn.text = trans["start_btn"]
        result_label.value = trans["result_label"]
        footer.value = trans["footer"]
        page.update()

    lang_dropdown.on_change = change_language

    def load_example(e):
        servers_field.value = "http://example.com:8080\nhttp://test.tv:12345\nhttp://backup.server:9999"
        page.update()

    def start_batch_test(e):
        servers = [s.strip() for s in servers_field.value.strip().splitlines() if s.strip()]
        username = username_field.value.strip()
        password = password_field.value.strip()

        if not servers or not username or not password:
            page.show_snack_bar(ft.SnackBar(content=ft.Text(trans["warning"]), bgcolor=ft.colors.RED_600))
            return

        result_area.value = ""
        if len(servers) > 1:
            result_area.value += trans["running"].format(len(servers)) + trans["only_first"]
        else:
            result_area.value += trans["running"].format(len(servers)) + trans["single"]
        page.update()

        start_btn.disabled = True
        progress_ring.visible = True
        page.update()

        resource_checked = False

        def run_tests():
            nonlocal resource_checked
            for i, server in enumerate(servers, 1):
                result_area.value += trans["detecting"].format(i, len(servers), server)
                page.update()

                check_res = (not resource_checked) and (i == 1 or len(servers) == 1)
                result_str, success = test_single_server(server, username, password, trans, check_res)
                
                result_area.value += result_str + "\n\n"
                page.update()

                if success and not resource_checked:
                    resource_checked = True
                
                time.sleep(0.4)

            progress_ring.visible = False
            start_btn.disabled = False
            result_area.value += "\n" + trans["complete"].format(len(servers)) + "\n"
            page.update()
            page.show_snack_bar(ft.SnackBar(content=ft.Text(trans["complete"].format(len(servers)), color=ft.colors.GREEN_400)))

        threading.Thread(target=run_tests, daemon=True).start()

    start_btn = ft.ElevatedButton(
        text=trans["start_btn"],
        icon=ft.icons.ROCKET_LAUNCH,
        on_click=start_batch_test,
        bgcolor=ft.colors.GREEN_700,
        color=ft.colors.WHITE,
        height=55,
        width=220,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12))
    )

    example_btn = ft.TextButton(trans["example"], on_click=load_example, icon=ft.icons.ADD_CIRCLE)

    result_label = ft.Text(trans["result_label"], weight="bold", size=16)
    footer = ft.Text(trans["footer"], color=ft.colors.GREY_500, size=13)

    page.add(
        ft.Column([
            title,
            ft.Row([lang_dropdown], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(height=10),
            username_field,
            password_field,
            ft.Row([servers_field, example_btn]),
            ft.Row([start_btn, progress_ring], alignment=ft.MainAxisAlignment.CENTER, spacing=30),
            result_label,
            result_area,
            footer
        ], spacing=15, expand=True, scroll=ft.ScrollMode.AUTO)
    )

# 本地运行测试
if __name__ == "__main__":
    ft.app(target=main, view=ft.WEB_BROWSER, port=8502)
