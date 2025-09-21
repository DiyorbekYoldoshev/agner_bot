# 🍅 O'zbek Pomodoro Telegram Bot

Bu bot Pomodoro texnikasi yordamida kunni samarali tashkil qilish uchun yaratilgan. To'liq o'zbek tilida va SQLite ma'lumotlar bazasi bilan ishlaydi.

## ✨ Asosiy Funksiyalar

### 🍅 Pomodoro Timer
- 25 daqiqalik ish seanslar
- 5 daqiqalik tanaffuslar
- Real-time timer va bildirishnomalar
- Vazifalar bilan bog'lash imkoniyati

### 📝 Vazifalar Boshqaruvi
- Kunlik vazifalar qo'shish
- Muhimlik darajasi belgilash (Yuqori/O'rta/Past)
- Vazifalarni bajarilgan deb belgilash
- Vazifalar ro'yxatini ko'rish

### 📊 To'liq Statistika
- **Kunlik hisobotlar**: bugungi Pomodoro seanslar, bajarilgan vazifalar, foizli ko'rsatkichlar
- **Haftalik statistika**: oxirgi 7 kunlik natijalar
- **Oylik hisobotlar**: oxirgi 30 kunlik umumiy ko'rsatkichlar
- Ish vaqti hisobi va progress tracking

### 🔧 Admin Paneli
- Barcha foydalanuvchilar ro'yxati
- Umumiy statistika va hisobotlar
- Barcha foydalanuvchilarga xabar yuborish
- Foydalanuvchilar faolligi monitoring

## 🚀 O'rnatish va Ishga Tushirish

### 1. Kerakli kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 2. Bot Token Olish
1. Telegram'da @BotFather ga murojaat qiling
2. `/newbot` komandasi bilan yangi bot yarating
3. Bot token'ini oling

### 3. Konfiguratsiya
`config.py` faylida quyidagi o'zgarishlarni qiling:

```python
BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"  # Sizning bot tokeningiz
ADMIN_IDS = [123456789, 987654321]  # Admin foydalanuvchi ID'lari
```

### 4. Botni Ishga Tushirish
```bash
python bot.py
```

## 📱 Foydalanish

### Asosiy Komandalar
- `/start` - Botni boshlash
- `/help` - Yordam ma'lumotlari
- `/admin` - Admin paneli (faqat adminlar uchun)

### Asosiy Funksiyalar
1. **🍅 Pomodoro** - 25 daqiqalik ish seansini boshlash
2. **📝 Vazifalar** - kunlik vazifalarni boshqarish
3. **📊 Statistika** - natijalarni ko'rish
4. **⚙️ Sozlamalar** - shaxsiy sozlamalar

## 🗄️ Ma'lumotlar Bazasi

Bot SQLite ma'lumotlar bazasidan foydalanadi va quyidagi jadvallarni yaratadi:

- `users` - Foydalanuvchilar ma'lumotlari
- `tasks` - Vazifalar
- `pomodoro_sessions` - Pomodoro seanslar
- `daily_stats` - Kunlik statistika

## 📈 Statistika Tizimi

### Kunlik Hisobotlar
- Bugungi Pomodoro seanslar soni
- Bajarilgan/jami vazifalar
- Bajarish foizi
- Umumiy ish vaqti

### Haftalik va Oylik
- Oxirgi 7/30 kunlik umumiy natijalar
- O'rtacha kunlik ko'rsatkichlar
- Progress tracking

## 🔐 Admin Funksiyalari

Adminlar quyidagi imkoniyatlarga ega:

1. **Foydalanuvchilar ro'yxati** - barcha foydalanuvchilar va ularning statistikasi
2. **Umumiy statistika** - butun bot bo'yicha umumiy ma'lumotlar
3. **Xabar yuborish** - barcha foydalanuvchilarga bir vaqtda xabar yuborish

## 🛠️ Texnik Tafsilotlar

- **Dasturlash tili**: Python 3.8+
- **Kutubxona**: python-telegram-bot 20.7
- **Ma'lumotlar bazasi**: SQLite
- **Asinxron ishlov berish**: asyncio

## 📝 Litsenziya

Bu loyiha MIT litsenziyasi ostida tarqatiladi.

## 🤝 Yordam va Qo'llab-quvvatlash

Agar savollaringiz bo'lsa yoki yordam kerak bo'lsa, iltimos bog'laning.

---

**Pomodoro texnikasi**: 25 daqiqa ish + 5 daqiqa tanaffus = maksimal samaradorlik! 🍅