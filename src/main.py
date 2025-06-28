import cv2
from pathlib import Path
import numpy as np
from matplotlib import pyplot as plt
from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk


def load_image(path):
    """Загружает изображение с поддержкой русских путей"""
    try:
        # Преобразуем путь в абсолютный
        abs_path = Path(path).absolute()

        # Способ 1: через OpenCV (для большинства случаев)
        img = cv2.imread(str(abs_path))
        if img is not None:
            return img

        # Способ 2: через PIL (если OpenCV не сработал)
        pil_img = Image.open(abs_path)
        return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось загрузить изображение: {str(e)}")
        return None


class ImageProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processor")
        self.image = None
        self.tk_img = None  # Для хранения ссылки на изображение
        self.processing = False  # Флаг для отслеживания обработки
        self.setup_ui()

        self.status_var = StringVar()
        self.status_var.set("Готов к работе")
        self.status_bar = Label(self.root, textvariable=self.status_var, bd=1, relief=SUNKEN, anchor=W)
        self.status_bar.pack(side=BOTTOM, fill=X)

    def update_status(self, message):
        """Обновляет статус"""
        self.status_var.set(message)
        self.root.update_idletasks()

    def show_success(self, message):
        """Показывает сообщение об успехе"""
        self.update_status(f"Успех: {message}")
        messagebox.showinfo("Успех", message)

    def show_error(self, message):
        """Показывает сообщение об ошибке"""
        self.update_status(f"Ошибка: {message}")
        messagebox.showerror("Ошибка", message)

    def setup_ui(self):
        # Кнопки для загрузки изображения
        Button(self.root, text="Загрузить изображение", command=self.load_image_dialog).pack(pady=5)
        Button(self.root, text="Сделать снимок с камеры", command=self.capture_from_camera).pack(pady=5)

        # Выбор канала
        Label(self.root, text="Выберите канал:").pack()
        self.channel_var = StringVar(value="red")
        frame_channels = Frame(self.root)
        frame_channels.pack()
        Radiobutton(frame_channels, text="Красный", variable=self.channel_var, value="red").pack(side=LEFT)
        Radiobutton(frame_channels, text="Зеленый", variable=self.channel_var, value="green").pack(side=LEFT)
        Radiobutton(frame_channels, text="Синий", variable=self.channel_var, value="blue").pack(side=LEFT)
        Button(self.root, text="Показать канал", command=self.show_channel).pack(pady=5)

        # Красная маска
        Label(self.root, text="Порог для красного:").pack()
        self.red_threshold = Scale(self.root, from_=0, to=255, orient=HORIZONTAL)
        self.red_threshold.pack()
        Button(self.root, text="Применить красную маску", command=self.apply_red_mask).pack(pady=5)

        # Повышение резкости
        Button(self.root, text="Повысить резкость", command=self.sharpen_image).pack(pady=5)

        # Рисование линии
        Label(self.root, text="Координаты линии (x1 y1 x2 y2):").pack()
        self.line_coords = Entry(self.root)
        self.line_coords.pack()
        Label(self.root, text="Толщина линии:").pack()
        self.line_width = Entry(self.root)
        self.line_width.insert(0, "1")  # Значение по умолчанию
        self.line_width.pack()
        Button(self.root, text="Нарисовать линию", command=self.draw_line).pack(pady=5)

        # Холст для изображений
        self.canvas = Canvas(self.root, width=600, height=400, bg='gray')
        self.canvas.pack()

    def load_image_dialog(self):
        if self.processing:
            self.show_error("Дождитесь завершения текущей операции")
            return

        self.processing = True
        self.update_status("Открытие диалога выбора файла...")

        try:
            path = filedialog.askopenfilename(
                title="Выберите изображение",
                filetypes=[("Image files", "*.jpg *.png *.jpeg *.bmp"), ("All files", "*.*")]
            )

            if path:
                self.update_status(f"Загрузка изображения: {path}")
                self.image = load_image(path)

                if self.image is not None:
                    self.display_image(self.image)
                    self.show_success(f"Изображение загружено: {Path(path).name}")
                else:
                    self.show_error("Не удалось загрузить изображение")
        except Exception as e:
            self.show_error(f"Ошибка при загрузке: {str(e)}")
        finally:
            self.processing = False

    def capture_from_camera(self):
        if self.processing:
            self.show_error("Дождитесь завершения текущей операции")
            return

        self.processing = True
        self.update_status("Подключение к камере...")

        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                self.show_error("Не удалось подключиться к камере")
                return

            self.update_status("Камера подключена. Делаем снимок...")
            ret, frame = cap.read()
            cap.release()

            if ret:
                self.image = frame
                self.display_image(self.image)
                self.show_success("Снимок с камеры сделан успешно")
            else:
                self.show_error("Не удалось получить изображение с камеры")
        except Exception as e:
            self.show_error(f"Ошибка камеры: {str(e)}")
        finally:
            self.processing = False

    def display_image(self, img):
        try:
            self.update_status("Подготовка изображения для отображения...")

            # Конвертируем в RGB для Tkinter
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)

            # Масштабируем изображение, если оно слишком большое
            max_width, max_height = 800, 600
            if img_pil.width > max_width or img_pil.height > max_height:
                img_pil.thumbnail((max_width, max_height), Image.LANCZOS)
                self.update_status("Изображение масштабировано для отображения")

            # Создаем PhotoImage
            self.tk_img = ImageTk.PhotoImage(img_pil)

            # Устанавливаем размер холста под изображение
            self.canvas.config(width=img_pil.width, height=img_pil.height)

            # Отображаем изображение
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)

            self.update_status("Изображение отображено")
        except Exception as e:
            self.show_error(f"Ошибка отображения: {str(e)}")

    def show_channel(self):
        if self.processing:
            self.show_error("Дождитесь завершения текущей операции")
            return

        if self.image is None:
            self.show_error("Сначала загрузите изображение")
            return

        self.processing = True
        self.update_status("Обработка выбранного канала...")

        try:
            channel = self.channel_var.get()
            channel_name = {"red": "Красный", "green": "Зеленый", "blue": "Синий"}[channel]

            if channel == "red":
                channel_img = self.image[:, :, 2]  # Красный канал
            elif channel == "green":
                channel_img = self.image[:, :, 1]  # Зеленый канал
            else:
                channel_img = self.image[:, :, 0]  # Синий канал

            plt.figure(figsize=(8, 6))
            plt.imshow(channel_img, cmap='gray')
            plt.title(f"{channel_name} канал")
            plt.show()

            self.show_success(f"Отображен {channel_name.lower()} канал")
        except Exception as e:
            self.show_error(f"Ошибка отображения канала: {str(e)}")
        finally:
            self.processing = False

    def apply_red_mask(self):
        if self.processing:
            self.show_error("Дождитесь завершения текущей операции")
            return

        if self.image is None:
            self.show_error("Сначала загрузите изображение")
            return

        self.processing = True
        self.update_status("Применение красной маски...")

        try:
            threshold = self.red_threshold.get()
            red_channel = self.image[:, :, 2]
            mask = (red_channel > threshold).astype(np.uint8) * 255

            plt.figure(figsize=(8, 6))
            plt.imshow(mask, cmap='gray')
            plt.title(f"Красная маска (порог = {threshold})")
            plt.show()

            self.show_success(f"Красная маска применена с порогом {threshold}")
        except Exception as e:
            self.show_error(f"Ошибка применения маски: {str(e)}")
        finally:
            self.processing = False

    def sharpen_image(self):
        if self.processing:
            self.show_error("Дождитесь завершения текущей операции")
            return

        if self.image is None:
            self.show_error("Сначала загрузите изображение")
            return

        self.processing = True
        self.update_status("Повышение резкости...")

        try:
            kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
            sharpened = cv2.filter2D(self.image, -1, kernel)
            self.display_image(sharpened)
            self.show_success("Резкость изображения повышена")
        except Exception as e:
            self.show_error(f"Ошибка повышения резкости: {str(e)}")
        finally:
            self.processing = False

    def draw_line(self):
        if self.processing:
            self.show_error("Дождитесь завершения текущей операции")
            return

        if self.image is None:
            self.show_error("Сначала загрузите изображение")
            return

        self.processing = True
        self.update_status("Рисование линии...")

        try:
            # Проверка и парсинг координат
            coords_text = self.line_coords.get().strip()
            if not coords_text:
                raise ValueError("Введите координаты линии")

            coords = list(map(int, coords_text.split()))
            if len(coords) != 4:
                raise ValueError("Введите 4 координаты (x1 y1 x2 y2)")

            x1, y1, x2, y2 = coords

            # Проверка и парсинг толщины линии
            width_text = self.line_width.get().strip()
            if not width_text:
                raise ValueError("Введите толщину линии")

            thickness = int(width_text)
            if thickness <= 0:
                raise ValueError("Толщина линии должна быть положительным числом")

            # Проверка, что координаты в пределах изображения
            h, w = self.image.shape[:2]
            if not (0 <= x1 < w and 0 <= y1 < h and 0 <= x2 < w and 0 <= y2 < h):
                raise ValueError(f"Координаты должны быть в пределах изображения (0-{w - 1}, 0-{h - 1})")

            # Рисование линии
            img_copy = self.image.copy()
            cv2.line(img_copy, (x1, y1), (x2, y2), (0, 255, 0), thickness)
            self.display_image(img_copy)

            self.show_success(f"Линия нарисована от ({x1},{y1}) до ({x2},{y2})")
        except ValueError as ve:
            self.show_error(f"Некорректный ввод: {str(ve)}")
        except Exception as e:
            self.show_error(f"Ошибка рисования линии: {str(e)}")
        finally:
            self.processing = False


if __name__ == "__main__":
    root = Tk()
    try:
        app = ImageProcessor(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Критическая ошибка", f"Программа завершена из-за ошибки: {str(e)}")