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
        self.setup_ui()

    def setup_ui(self):
        # Кнопки для загрузки изображения
        Button(self.root, text="Загрузить изображение", command=self.load_image_dialog).pack()
        Button(self.root, text="Сделать снимок с камеры", command=self.capture_from_camera).pack()

        # Выбор канала
        self.channel_var = StringVar(value="red")
        Radiobutton(self.root, text="Красный", variable=self.channel_var, value="red").pack()
        Radiobutton(self.root, text="Зеленый", variable=self.channel_var, value="green").pack()
        Radiobutton(self.root, text="Синий", variable=self.channel_var, value="blue").pack()
        Button(self.root, text="Показать канал", command=self.show_channel).pack()

        # Красная маска
        Label(self.root, text="Порог для красного:").pack()
        self.red_threshold = Scale(self.root, from_=0, to=255, orient=HORIZONTAL)
        self.red_threshold.pack()
        Button(self.root, text="Применить красную маску", command=self.apply_red_mask).pack()

        # Повышение резкости
        Button(self.root, text="Повысить резкость", command=self.sharpen_image).pack()

        # Рисование линии
        Label(self.root, text="Координаты линии (x1 y1 x2 y2):").pack()
        self.line_coords = Entry(self.root)
        self.line_coords.pack()
        Label(self.root, text="Толщина линии:").pack()
        self.line_width = Entry(self.root)
        self.line_width.pack()
        Button(self.root, text="Нарисовать линию", command=self.draw_line).pack()

        # Холст для изображения
        self.canvas = Canvas(self.root, width=600, height=400)
        self.canvas.pack()

    def load_image_dialog(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg")])
        if path:
            self.image = load_image(path)  # Используем нашу функцию загрузки
            if self.image is not None:
                self.display_image(self.image)

    def capture_from_camera(self):
        try:
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            cap.release()
            if ret:
                self.image = frame
                self.display_image(self.image)
            else:
                messagebox.showerror("Ошибка", "Не удалось подключиться к камере")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка камеры: {e}. Проверьте подключение.")

    def display_image(self, img):
        # Конвертируем в RGB для Tkinter
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)

        # Создаем PhotoImage в оригинальном размере
        self.tk_img = ImageTk.PhotoImage(img_pil)

        # Устанавливаем размер холста под изображение
        self.canvas.config(width=img_pil.width, height=img_pil.height)

        # Отображаем изображение
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)

    def show_channel(self):
        if self.image is None:
            messagebox.showerror("Ошибка", "Сначала загрузите изображение")
            return

        channel = self.channel_var.get()
        if channel == "red":
            channel_img = self.image[:, :, 2]  # Красный канал
        elif channel == "green":
            channel_img = self.image[:, :, 1]  # Зеленый канал
        else:
            channel_img = self.image[:, :, 0]  # Синий канал

        plt.imshow(channel_img, cmap='gray')
        plt.title(f"{channel.capitalize()} Channel")
        plt.show()

    def apply_red_mask(self):
        if self.image is None:
            messagebox.showerror("Ошибка", "Сначала загрузите изображение")
            return

        threshold = self.red_threshold.get()
        red_channel = self.image[:, :, 2]
        mask = (red_channel > threshold).astype(np.uint8) * 255
        plt.imshow(mask, cmap='gray')
        plt.title("Red Mask")
        plt.show()

    def sharpen_image(self):
        if self.image is None:
            messagebox.showerror("Ошибка", "Сначала загрузите изображение")
            return

        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        sharpened = cv2.filter2D(self.image, -1, kernel)
        self.display_image(sharpened)

    def draw_line(self):
        if self.image is None:
            messagebox.showerror("Ошибка", "Сначала загрузите изображение")
            return

        try:
            coords = list(map(int, self.line_coords.get().split()))
            x1, y1, x2, y2 = coords
            thickness = int(self.line_width.get())
            img_copy = self.image.copy()
            cv2.line(img_copy, (x1, y1), (x2, y2), (0, 255, 0), thickness)
            self.display_image(img_copy)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Некорректный ввод: {e}")


if __name__ == "__main__":
    root = Tk()
    app = ImageProcessor(root)
    root.mainloop()