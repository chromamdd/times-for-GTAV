import os
import re
import sys
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

import customtkinter as ctk
from tkinterdnd2 import TkinterDnD, DND_FILES


def _resource_path(relative_path):
    """Путь к файлу рядом с exe (PyInstaller) или со скриптом."""
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)


# Тёмная тема и закруглённые углы
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class CTkDnD(ctk.CTk, TkinterDnD.DnDWrapper):
    """Окно CTk с поддержкой перетаскивания файлов."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

def get_cycle_name(filename):
    """
    Получает правильное имя цикла для файла.
    
    Args:
        filename: Имя файла
    """
    base_filename = os.path.basename(filename)
    
    cycle_names = {
        "underwater_deep.xml": "underwater_deep",
        "w_blizzard.xml": "BLIZZARD",
        "w_clear.xml": "CLEAR",
        "w_clearing.xml": "CLEARING",
        "w_clouds.xml": "CLOUDS",
        "w_extrasunny.xml": "EXTRASUNNY",
        "w_foggy.xml": "FOGGY",
        "w_halloween.xml": "HALLOWEEN",
        "w_neutral.xml": "NEUTRAL",
        "w_overcast.xml": "OVERCAST",
        "w_rain.xml": "RAIN",
        "w_rainhalloween.xml": "RAIN_HALLOWEEN",
        "w_smog.xml": "SMOG",
        "w_snow.xml": "SNOW",
        "w_snowhalloween.xml": "SNOW_HALLOWEEN",
        "w_snowlight.xml": "SNOWLIGHT",
        "w_thunder.xml": "THUNDER",
        "w_xmas.xml": "XMAS"
    }
    
    if base_filename in cycle_names:
        return cycle_names[base_filename]
    
    name = base_filename.replace('.xml', '')
    if name.startswith('w_'):
        name = name[2:]
    return name.upper()

def generate_weather_files(input_file="ВЫБЕРИ ФАЙЛ", log_callback=None):
    """
    Генерирует остальные XML файлы на основе одного
    
    Args:
        input_file: Путь к исходному файлу
        log_callback: Функция для вывода сообщений (принимает строку)
    """
    
    def log(message):
        if log_callback:
            log_callback(message)
        else:
            print(message)
    
    weather_files = [
        "underwater_deep.xml",
        "w_blizzard.xml",
        "w_clear.xml",
        "w_clearing.xml",
        "w_clouds.xml",
        "w_extrasunny.xml",  
        "w_foggy.xml",
        "w_halloween.xml",
        "w_neutral.xml",
        "w_overcast.xml",
        "w_rain.xml",
        "w_rainhalloween.xml",
        "w_smog.xml",
        "w_snow.xml",
        "w_snowhalloween.xml",
        "w_snowlight.xml",
        "w_thunder.xml",
        "w_xmas.xml"
    ]
    
    if not os.path.exists(input_file):
        error_msg = f"Ошибка: Файл {input_file} не найден!"
        log(error_msg)
        return False
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        error_msg = f"Ошибка при чтении файла {input_file}: {e}"
        log(error_msg)
        return False
    
    pattern = r'<cycle\s+name="([^"]+)"'
    match = re.search(pattern, content)
    
    if not match:
        log("Предупреждение: Не найдена строка <cycle name=\"...\"> в исходном файле")
        log("Продолжаю генерацию, используя имя файла без расширения для замены")
    
    output_dir = "timecycle"
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            log(f"Создана папка: {output_dir}")
        except Exception as e:
            error_msg = f"Ошибка при создании папки {output_dir}: {e}"
            log(error_msg)
            return False
    else:
        log(f"Используется папка: {output_dir}")
    
    created_count = 0
    errors_count = 0
    
    for filename in weather_files:
        base_input = os.path.basename(input_file)
        if filename == base_input:
            continue
        
        cycle_name = get_cycle_name(filename)
        
        if match:
            new_content = re.sub(pattern, f'<cycle name="{cycle_name}"', content, count=1)
        else:
            new_content = re.sub(
                r'<cycle\s+name="[^"]*"',
                f'<cycle name="{cycle_name}"',
                content,
                count=1
            )
        
        output_path = os.path.join(output_dir, filename)
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            log(f"✓ Создан файл: {output_path} (name=\"{cycle_name}\")")
            created_count += 1
        except Exception as e:
            error_msg = f"✗ Ошибка при создании файла {output_path}: {e}"
            log(error_msg)
            errors_count += 1
    
    log(f"\n{'='*50}")
    log(f"Генерация завершена!")
    log(f"Создано файлов: {created_count}")
    if errors_count > 0:
        log(f"Ошибок: {errors_count}")
    log(f"{'='*50}")
    
    return errors_count == 0

class WeatherFileGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CHROMA TIMES")
        self.root.geometry("640x560")
        self.root.minsize(520, 480)
        # Тёмный фон окна (тот же цвет для верхней плашки — без разделения)
        self._bg_color = ("#2b2b2b", "#1a1a1a")
        self.root.configure(fg_color=self._bg_color)

        # Своя верхняя плашка без логотипа, в цвет фона — перетаскивание окна
        top_bar = ctk.CTkFrame(
            root,
            height=52,
            fg_color=self._bg_color,
            corner_radius=0,
        )
        top_bar.pack(fill=tk.X)
        top_bar.pack_propagate(False)
        top_bar.bind("<ButtonPress-1>", self._start_drag)
        top_bar.bind("<B1-Motion>", self._on_drag)

        top_inner = ctk.CTkFrame(top_bar, fg_color="transparent")
        top_inner.pack(fill=tk.BOTH, expand=True, padx=16, pady=6)
        top_inner.bind("<ButtonPress-1>", self._start_drag)
        top_inner.bind("<B1-Motion>", self._on_drag)

        # Скруглённая рамка только вокруг текста (как у крестика), компактная при выделении
        title_box = ctk.CTkFrame(
            top_inner,
            fg_color=("#383838", "#282828"),
            corner_radius=6,
            width=165,
            height=34,
        )
        title_box.pack(side=tk.LEFT)
        title_box.pack_propagate(False)
        title_box.bind("<ButtonPress-1>", self._start_drag)
        title_box.bind("<B1-Motion>", self._on_drag)
        self._title_box = title_box
        # Текст в своём Frame поверх скруглённой рамки
        title_label_frame = tk.Frame(top_inner, bg="#282828")
        title_label_frame.place(in_=top_inner, x=3, y=3, width=159, height=28)
        title_label = tk.Label(
            title_label_frame,
            text="t.me/chromamods",
            font=("Segoe UI", 12, "bold"),
            fg="#e0e0e0",
            bg="#282828",
            activeforeground="#e0e0e0",
            activebackground="#282828",
            cursor="hand2",
        )
        title_label.pack(expand=True, padx=10, pady=4)
        self._title_label_frame = title_label_frame
        self._title_label = title_label
        title_label_frame.bind("<ButtonPress-1>", self._start_drag)
        title_label_frame.bind("<B1-Motion>", self._on_drag)
        title_label_frame.bind("<ButtonRelease-1>", self._on_title_release)
        title_label_frame.bind("<Enter>", self._on_title_enter)
        title_label_frame.bind("<Leave>", self._on_title_leave)
        title_label.bind("<ButtonPress-1>", self._start_drag)
        title_label.bind("<B1-Motion>", self._on_drag)
        title_label.bind("<ButtonRelease-1>", self._on_title_release)
        title_label.bind("<Enter>", self._on_title_enter)
        title_label.bind("<Leave>", self._on_title_leave)

        # Скруглённый квадрат вокруг кнопки закрытия — чуть ярче фона
        close_box = ctk.CTkFrame(
            top_inner,
            fg_color=("#383838", "#282828"),
            corner_radius=6,
        )
        close_box.pack(side=tk.RIGHT)
        ctk.CTkButton(
            close_box,
            text="\u00d7",
            width=28,
            height=24,
            corner_radius=5,
            font=ctk.CTkFont(size=18),
            fg_color="transparent",
            hover_color=("#454545", "#353535"),
            text_color=("#e0e0e0", "#e0e0e0"),
            command=root.destroy,
        ).pack(padx=3, pady=3)

        # Тонкая тёмно-серая линия между верхней плашкой и контентом
        sep = tk.Frame(root, height=2, bg="#454545")
        sep.pack(fill=tk.X)
        sep.pack_propagate(False)

        # Блок выбора файла
        file_frame = ctk.CTkFrame(root, fg_color="transparent")
        file_frame.pack(pady=12, padx=24, fill=tk.X)

        ctk.CTkLabel(
            file_frame,
            text="Исходный файл:",
            font=ctk.CTkFont(size=12),
            width=100,
            anchor="w",
        ).pack(side=tk.LEFT, padx=(0, 8))

        self.file_path_var = tk.StringVar(value="w_extrasunny.xml")
        file_entry = ctk.CTkEntry(
            file_frame,
            textvariable=self.file_path_var,
            width=320,
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=12),
            placeholder_text="Путь к XML файлу...",
        )
        file_entry.pack(side=tk.LEFT, padx=(0, 8), fill=tk.X, expand=True)

        browse_btn = ctk.CTkButton(
            file_frame,
            text="Обзор...",
            command=self.browse_file,
            width=90,
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=12),
            fg_color=("#ffffff", "#e8e8e8"),
            text_color=("#1a1a1a", "#1a1a1a"),
            hover_color=("#e0e0e0", "#d0d0d0"),
        )
        browse_btn.pack(side=tk.LEFT)

        # Кнопка генерации
        generate_btn = ctk.CTkButton(
            root,
            text="Сгенерировать файлы",
            command=self.generate_files,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=44,
            corner_radius=10,
            fg_color=("#ffffff", "#e8e8e8"),
            text_color=("#1a1a1a", "#1a1a1a"),
            hover_color=("#e0e0e0", "#d0d0d0"),
        )
        generate_btn.pack(pady=18)

        # Лог
        log_label = ctk.CTkLabel(
            root,
            text="Лог выполнения:",
            font=ctk.CTkFont(size=12),
            anchor="w",
        )
        log_label.pack(anchor=tk.W, padx=24, pady=(0, 6))

        self.log_text = ctk.CTkTextbox(
            root,
            height=220,
            corner_radius=10,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color=("#252525", "#1e1e1e"),
            text_color=("#c0c0c0", "#c0c0c0"),
            wrap="word",
        )
        self.log_text.pack(pady=(0, 12), padx=24, fill=tk.BOTH, expand=True)

        # Строка состояния
        self.status_var = tk.StringVar(value="Готов к работе")
        status_frame = ctk.CTkFrame(root, fg_color=("#333333", "#252525"), height=32, corner_radius=6)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=24, pady=(0, 16))
        status_frame.pack_propagate(False)
        status_bar = ctk.CTkLabel(
            status_frame,
            textvariable=self.status_var,
            font=ctk.CTkFont(size=11),
            text_color=("#a0a0a0", "#909090"),
            anchor="w",
        )
        status_bar.pack(side=tk.LEFT, padx=12, pady=6, fill=tk.X, expand=True)

        # Перетаскивание файла в окно
        try:
            root.drop_target_register(DND_FILES)
            root.dnd_bind("<<Drop>>", self._on_drop_file)
        except Exception:
            pass  # DnD недоступен на этой платформе

        # Убираем системный заголовок и иконку — своя плашка того же цвета
        self.root.overrideredirect(True)
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        w, h = 640, 560
        x = max(0, (sw - w) // 2)
        y = max(0, (sh - h) // 2 - 20)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _start_drag(self, event):
        self._did_drag = False
        self._drag_start_x = event.x_root
        self._drag_start_y = event.y_root
        self._win_start_x = self.root.winfo_rootx()
        self._win_start_y = self.root.winfo_rooty()

    def _on_drag(self, event):
        self._did_drag = True
        dx = event.x_root - self._drag_start_x
        dy = event.y_root - self._drag_start_y
        self.root.geometry(f"+{self._win_start_x + dx}+{self._win_start_y + dy}")
        self._win_start_x += dx
        self._win_start_y += dy
        self._drag_start_x = event.x_root
        self._drag_start_y = event.y_root

    def _on_title_enter(self, event):
        # Как у крестика: плашка слегка светлеет при наведении
        self._title_box.configure(fg_color=("#454545", "#353535"))
        self._title_label_frame["bg"] = "#353535"
        self._title_label["bg"] = "#353535"

    def _on_title_leave(self, event):
        self._title_box.configure(fg_color=("#383838", "#282828"))
        self._title_label_frame["bg"] = "#282828"
        self._title_label["bg"] = "#282828"

    def _on_title_release(self, event):
        if not getattr(self, "_did_drag", True):
            webbrowser.open("https://t.me/chromamods")

    def _on_drop_file(self, event):
        """Обработчик перетаскивания файла в окно."""
        data = event.data
        if not data:
            return
        # Пути приходят в формате Tcl (с фигурными скобками), разбираем через splitlist
        try:
            paths = self.root.tk.splitlist(data)
        except Exception:
            path = data.strip().strip("{}")
            paths = [path] if path else []
        path = paths[0] if paths else ""
        if path and (path.lower().endswith(".xml") or os.path.isfile(path)):
            self.file_path_var.set(path)
            self.status_var.set("Файл выбран: " + os.path.basename(path))
    
    def browse_file(self):
        """Открывает диалог выбора файла"""
        filename = filedialog.askopenfilename(
            title="Выберите исходный XML файл",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        if filename:
            self.file_path_var.set(filename)
    
    def log(self, message):
        """Добавляет сообщение в лог"""
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.root.update()
    
    def generate_files(self):
        """Запускает генерацию файлов"""
        self.log_text.delete("1.0", "end")
        
        input_file = self.file_path_var.get().strip()
        if not input_file:
            messagebox.showerror("Ошибка", "Пожалуйста, укажите исходный файл!")
            return
        
        self.status_var.set("Генерация файлов...")
        self.log(f"Начинаю генерацию файлов из: {input_file}\n")
        
        input_dir = os.path.dirname(input_file)
        original_dir = os.getcwd()
        
        if input_dir:
            os.chdir(input_dir)
            input_file = os.path.basename(input_file)
        
        try:
            success = generate_weather_files(input_file, self.log)
            
            if input_dir:
                os.chdir(original_dir)
            
            if success:
                self.status_var.set("Генерация завершена успешно!")
                messagebox.showinfo("Успех", "Все файлы успешно созданы!")
            else:
                self.status_var.set("Генерация завершена с ошибками")
                messagebox.showwarning("Предупреждение", 
                                     "Генерация завершена, но были ошибки. Проверьте лог.")
        except Exception as e:
            self.log(f"\nКРИТИЧЕСКАЯ ОШИБКА: {e}")
            self.status_var.set("Ошибка генерации")
            messagebox.showerror("Ошибка", f"Произошла ошибка:\n{e}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        generate_weather_files(input_file)
    else:
        root = CTkDnD()
        app = WeatherFileGeneratorGUI(root)
        root.mainloop()

