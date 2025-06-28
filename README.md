# Инструкция по запуску приложения

## Требования
- Python 3.8+
- Виртуальное окружение (рекомендуется)

## Установка
1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/Arisha-solnyshko/Practika
   cd ваш-репозиторий
   ```

2. Создайте и активируйте виртуальное окружение:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   .\venv\Scripts\activate   # Windows
   ```

3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

## Запуск
```bash
python src/main.py
```

## Дополнительно
- Для работы с камерой убедитесь, что устройство подключено.
- Поддерживаемые форматы изображений: `.jpg`, `.png`.