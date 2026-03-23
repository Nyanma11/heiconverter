import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import os
import ctypes
import winreg
from PIL import Image
from pillow_heif import register_heif_opener

# 高DPI対応
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

register_heif_opener()

def is_dark_mode():
    try:
        registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        return value == 0
    except Exception:
        return False

class HeicConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HEIC to JPEG Converter")
        self.root.geometry("450x250")
        
        # ダークモード判定
        dark = is_dark_mode()
        
        # --- タイトルバーをダークモードにする魔法 (Windows 10/11用) ---
        if dark:
            self.root.update() # ウィンドウ情報を確定させる
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            set_status = ctypes.c_int(1)
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, 
                ctypes.byref(set_status), ctypes.sizeof(set_status)
            )

        # カラー設定
        if dark:
            self.bg_color = "#2d2d2d"; self.frame_bg = "#3d3d3d"
            self.text_color = "#ffffff"; self.accent_color = "#005a9e"
        else:
            self.bg_color = "#f0f0f0"; self.frame_bg = "#ffffff"
            self.text_color = "#000000"; self.accent_color = "#0078d7"
        
        self.root.configure(bg=self.bg_color)

        # UI
        self.drop_frame = tk.Frame(root, bg=self.frame_bg, bd=2, relief="groove")
        self.drop_frame.pack(padx=20, pady=20, fill="both", expand=True)

        self.label = tk.Label(self.drop_frame, text="ここにHEICをドロップ\n(またはボタンで選択)", 
                             bg=self.frame_bg, fg=self.text_color, font=("Meiryo", 11))
        self.label.pack(expand=True)

        self.btn_select = tk.Button(self.drop_frame, text="ファイルを選択", 
                                   command=self.select_files,
                                   bg=self.accent_color, fg="white", relief="flat")
        self.btn_select.pack(pady=10)

        self.ver_label = tk.Label(root, text="v1.1.0", bg=self.bg_color, 
                                 fg="#888888", font=("Arial", 8))
        self.ver_label.place(relx=1.0, rely=1.0, anchor="se", x=-5, y=-2)

        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.handle_drop)

    # ... (process_files, select_files, handle_drop はそのまま) ...
    def process_files(self, file_paths, open_explorer=False):
        if not file_paths: return
        success_count = 0
        last_dir = ""
        for path in file_paths:
            path = path.strip('{}')
            if path.lower().endswith(".heic"):
                try:
                    last_dir = os.path.dirname(path)
                    output_path = os.path.join(last_dir, f"{os.path.splitext(os.path.basename(path))[0]}.jpg")
                    with Image.open(path) as image:
                        image.convert("RGB").save(output_path, "JPEG", quality=90)
                    success_count += 1
                except Exception: pass
        if success_count > 0:
            messagebox.showinfo("完了", f"{success_count}枚の変換が完了しました")
            if open_explorer and last_dir: os.startfile(last_dir)

    def select_files(self):
        paths = filedialog.askopenfilenames(filetypes=[("HEIC files", "*.heic")])
        self.process_files(paths, open_explorer=True)

    def handle_drop(self, event):
        files = self.root.splitlist(event.data)
        self.process_files(files, open_explorer=False)

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = HeicConverterApp(root)
    root.mainloop()