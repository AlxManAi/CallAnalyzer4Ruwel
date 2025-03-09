import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.audio import MIMEAudio
from email.utils import encode_rfc2231
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import time

# Настройки SMTP-сервера Gmail
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587  # Порт для TLS


# Функция для отправки письма
def send_email(file_path, recipient, sender_email, sender_password):
    try:
        # Создание письма
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = 'Звонки от клиентов сайта Ruwel'

        with open(file_path, 'rb') as f:
            part = MIMEAudio(f.read(), _subtype='mp3')

        # Кодирование имени файла для Content-Disposition
        encoded_filename = encode_rfc2231(os.path.basename(file_path), charset='utf-8')
        part.add_header('Content-Disposition', f'attachment; filename*=utf-8\'\'{encoded_filename}')

        msg.attach(part)

        # Подключение к SMTP-серверу
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Защита соединения через TLS
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient, msg.as_string())
        server.quit()

        return True
    except smtplib.SMTPAuthenticationError:
        return "Ошибка аутентификации. Проверьте логин и приложение-пароль."
    except Exception as e:
        return str(e)


# Функция для выбора папки с файлами
def select_folder():
    folder_path = filedialog.askdirectory()
    folder_entry.delete(0, tk.END)
    folder_entry.insert(0, folder_path)


# Функция для начала отправки
def start_sending():
    global sent_count  # Глобальная переменная для счетчика отправленных файлов
    sent_count = 0  # Сброс счетчика

    folder_path = folder_entry.get()
    recipient = recipient_entry.get()
    sender_email = sender_email_entry.get()
    sender_password = sender_password_entry.get()

    if not folder_path or not recipient or not sender_email or not sender_password:
        messagebox.showerror("Ошибка", "Заполните все поля!")
        return

    files = [f for f in os.listdir(folder_path) if f.endswith('.mp3')]
    if not files:
        messagebox.showinfo("Информация", "В выбранной папке нет MP3-файлов.")
        return

    log_text.config(state=tk.NORMAL)
    log_text.delete(1.0, tk.END)

    # Блокировка кнопки "Начать отправку"
    send_button.config(state=tk.DISABLED)

    # Отправка каждого файла по отдельности
    total_files = len(files)  # Общее количество файлов
    for idx, file in enumerate(files, start=1):
        file_path = os.path.join(folder_path, file)
        result = send_email(file_path, recipient, sender_email, sender_password)
        if result is True:
            log_text.insert(tk.END, f"[{idx}/{total_files}] Файл {file} успешно отправлен.\n")
            sent_count += 1
        else:
            log_text.insert(tk.END, f"[{idx}/{total_files}] Ошибка при отправке файла {file}: {result}\n")

        # Добавляем задержку между отправками (например, 30 секунд)
        log_text.insert(tk.END, "Ожидание 30 секунд перед следующей отправкой...\n")
        log_text.update_idletasks()  # Обновляем GUI во время ожидания
        time.sleep(30)  # Задержка в 30 секунд

    log_text.config(state=tk.DISABLED)

    # Разблокировка кнопки "Начать отправку"
    send_button.config(state=tk.NORMAL)

    # Сообщение о завершении
    messagebox.showinfo("Готово", f"Отправка завершена! Отправлено {sent_count} файлов.")


# Создание окна
root = tk.Tk()
root.title("Отправка MP3 через Gmail")

# Элементы интерфейса
tk.Label(root, text="Папка с файлами:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
folder_entry = tk.Entry(root, width=50)
folder_entry.grid(row=0, column=1, padx=10, pady=5)
tk.Button(root, text="Выбрать папку", command=select_folder).grid(row=0, column=2, padx=10, pady=5)

tk.Label(root, text="Email получателя:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
recipient_entry = tk.Entry(root, width=50)
recipient_entry.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Ваш Email (Gmail):").grid(row=2, column=0, sticky="w", padx=10, pady=5)
sender_email_entry = tk.Entry(root, width=50)
sender_email_entry.grid(row=2, column=1, padx=10, pady=5)

tk.Label(root, text="Приложение-пароль:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
sender_password_entry = tk.Entry(root, width=50, show="*")
sender_password_entry.grid(row=3, column=1, padx=10, pady=5)

send_button = tk.Button(root, text="Начать отправку", command=start_sending)
send_button.grid(row=4, column=1, pady=10)

log_text = scrolledtext.ScrolledText(root, width=80, height=10, state=tk.DISABLED)
log_text.grid(row=5, column=0, columnspan=3, padx=10, pady=5)

# Глобальная переменная для счетчика отправленных файлов
sent_count = 0

# Запуск приложения
root.mainloop()