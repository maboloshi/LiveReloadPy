"""
Sublime Text 插件：LiveReloadPy
增强版 - 专为前端开发者优化
支持：项目级配置、多平台兼容、端口占用检测、自动路径转换
"""

import os
import threading
import webbrowser
import sublime
import sublime_plugin
import socket
import json
from livereload import Server

# 加载插件设置
settings = sublime.load_settings("LiveReloadPy.sublime-settings")


class LiveServerController:
    """管理 livereload 服务器生命周期和状态"""
    _server = None
    _thread = None
    _folder = None
    _port = None

    STATUS_KEY = "live_server_status"
    CLEAR_DELAY_MS = 3000  # 状态栏消息显示时间

    @classmethod
    def is_running(cls):
        return cls._server is not None

    @classmethod
    def get_project_settings(cls, folder):
        """读取项目级配置文件"""
        config_path = os.path.join(folder, ".livereload.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"读取项目配置错误: {e}")
        return {}

    @classmethod
    def get_effective_setting(cls, key, default):
        """获取有效设置值（优先项目级配置）"""
        folder_settings = cls.get_project_settings(cls._folder) if cls._folder else {}
        return folder_settings.get(key, settings.get(key, default))

    @classmethod
    def is_port_available(cls, port):
        """检测端口是否可用"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("127.0.0.1", port)) != 0

    @classmethod
    def start_server(cls, folder):
        """启动 livereload 服务器"""
        if not folder:
            cls.update_status("❌ 启动失败: 路径为空")
            return False

        if cls.is_running():
            cls.update_status("⚠️ livereload 已在运行")
            return False

        cls._folder = folder
        port = cls.get_effective_setting("port", 35729)
        open_browser = cls.get_effective_setting("open_browser_on_start", False)
        watch_exts = cls.get_effective_setting("watch_extensions", [".html", ".htm", ".css", ".js"])
        ignored_dirs = cls.get_effective_setting("ignore_dirs", [".git", ".svn", "node_modules"])

        if not cls.is_port_available(port):
            cls.update_status(f"❌ 端口 {port} 被占用")
            return False

        def run_server():
            """在独立线程中运行服务器"""
            try:
                cls._server = Server()

                # 添加监视模式（优化性能）
                for ext in watch_exts:
                    # 使用递归匹配模式，提高效率
                    pattern = os.path.join("**", f"*{ext}")
                    cls._server.watch(
                        os.path.join(folder, pattern),
                        ignore=lambda path: any(ignore_dir in path for ignore_dir in ignored_dirs)
                    )

                # 启动服务器
                cls._server.serve(
                    root=folder,
                    port=port,
                    open_url_delay=0 if open_browser else None,
                    debug=cls.get_effective_setting("debug_mode", False)
                )
            except Exception as e:
                cls.update_status(f"❌ 启动失败: {e}")
                cls._server = None
                cls._thread = None

        cls._thread = threading.Thread(target=run_server, daemon=True)
        cls._thread.start()
        cls._port = port
        cls.update_status(f"✅ livereload 启动: http://127.0.0.1:{port}")
        return True

    @classmethod
    def stop_server(cls):
        """停止 livereload 服务器"""
        if not cls.is_running():
            cls.update_status("⚠️ livereload 未运行")
            return

        # 停止服务器
        if hasattr(cls._server, 'application') and hasattr(cls._server.application, 'io_loop'):
            try:
                cls._server.application.io_loop.add_callback(
                    cls._server.application.io_loop.stop
                )
            except Exception as e:
                print(f"停止服务器时出错: {e}")

        cls._server = None
        cls._thread = None
        cls.update_status("🛑 livereload 已停止")

    @classmethod
    def open_current_file(cls, view):
        """在浏览器中打开当前文件"""
        if not cls.is_running():
            cls.update_status("⚠️ 服务未启动")
            return

        file_path = view.file_name()
        if not file_path:
            cls.update_status("❌ 文件路径无效")
            return

        # 计算相对于服务器根目录的路径
        try:
            rel_path = os.path.relpath(file_path, cls._folder)
            # 转换路径分隔符为URL格式
            url_path = rel_path.replace(os.sep, '/')
            url = f"http://127.0.0.1:{cls._port}/{url_path}"

            webbrowser.open_new_tab(url)
            cls.update_status(f"🌐 打开: {url}")
        except ValueError:
            cls.update_status("❌ 文件不在项目目录内")

    @classmethod
    def add_single_file_watch(cls, view):
        """添加单独文件监视"""
        if not cls.is_running():
            cls.update_status("⚠️ 请先启动服务器")
            return

        file_path = view.file_name()
        if not file_path:
            cls.update_status("❌ 文件路径无效")
            return

        try:
            # 添加文件到监视列表
            cls._server.watch(file_path)
            cls.update_status(f"👁️ 已添加单独监视: {os.path.basename(file_path)}")
        except Exception as e:
            cls.update_status(f"❌ 添加监视失败: {e}")

    @classmethod
    def update_status(cls, msg):
        """更新状态栏信息"""
        window = sublime.active_window()
        if not window:
            return
        for view in window.views():
            view.set_status(cls.STATUS_KEY, msg)
        sublime.set_timeout(lambda: cls.clear_status(), cls.CLEAR_DELAY_MS)

    @classmethod
    def clear_status(cls):
        """清除状态栏信息"""
        window = sublime.active_window()
        if not window:
            return
        for view in window.views():
            view.erase_status(cls.STATUS_KEY)


class StartLiveReloadCommand(sublime_plugin.WindowCommand):
    """启动 livereload 服务器"""
    def run(self):
        # 尝试获取项目文件夹或当前文件所在目录
        folders = self.window.folders()
        if folders:
            folder = folders[0]
        else:
            view = self.window.active_view()
            folder = os.path.dirname(view.file_name()) if view and view.file_name() else None

        if folder:
            LiveServerController.start_server(folder)
        else:
            sublime.status_message("无法确定项目目录")

    def is_enabled(self):
        return not LiveServerController.is_running()


class StopLiveReloadCommand(sublime_plugin.WindowCommand):
    """停止 livereload 服务器"""
    def run(self):
        LiveServerController.stop_server()

    def is_enabled(self):
        return LiveServerController.is_running()


class OpenInLiveReloadCommand(sublime_plugin.TextCommand):
    """在浏览器中打开当前文件"""
    def run(self, edit):
        LiveServerController.open_current_file(self.view)

    def is_enabled(self):
        return LiveServerController.is_running()


class AddSingleFileWatchCommand(sublime_plugin.TextCommand):
    """添加单独文件监视命令"""
    def run(self, edit):
        LiveServerController.add_single_file_watch(self.view)


class OpenLiveReloadSettingsCommand(sublime_plugin.ApplicationCommand):
    """打开插件设置"""
    def run(self):
        sublime.run_command("edit_settings", {
            "base_file": "${packages}/LiveReloadPy/LiveReloadPy.sublime-settings"
        })


class LiveReloadListener(sublime_plugin.EventListener):
    """事件监听器，提供自动保存提示"""
    def on_post_save(self, view):
        if LiveServerController.is_running():
            file_ext = os.path.splitext(view.file_name() or '')[1].lower()
            watch_exts = LiveServerController.get_effective_setting(
                "watch_extensions", [".html", ".htm", ".css", ".js"]
            )

            if file_ext in watch_exts:
                view.set_status("live_reload_saved", "✔️ 文件已保存，LiveReload 将自动刷新")
                sublime.set_timeout(
                    lambda: view.erase_status("live_reload_saved"),
                    2000
                )
