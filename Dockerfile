FROM python:3.11-slim

# تنظیمات محیط
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# نصب وابستگی‌های سیستم
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# کپی فایل‌های مورد نیاز
COPY requirements.txt .
COPY .env.example .env

# نصب وابستگی‌های پایتون
RUN pip install --no-cache-dir -r requirements.txt

# کپی سایر فایل‌ها
COPY . .

# ایجاد دایرکتوری برای دیتابیس
RUN mkdir -p /app/data

# پورت
EXPOSE 8080

# دستور اجرا
CMD ["python", "bot.py"]
