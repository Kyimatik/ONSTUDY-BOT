# 🤖 Onstudy Bot

**Onstudy Bot** is a fully asynchronous Telegram bot built for the **Onstudy** educational platform.  
It’s designed to enhance user interaction, streamline communication with sales agents via CRM, and provide admins with powerful tools and automation.

## 🚀 Features

- Fully **asynchronous architecture** with `FastAPI` and `Aiogram 3`
- Secure **SSL certificate** running on **Nginx** with a **custom domain**
- Seamless **AMO CRM integration** – allows sales team to interact with users in real time
- Admin commands:
  - View user statistics
  - Broadcast messages
  - Access logs and analytics
- **Daily database backups**
- Clean and user-friendly **message design**
- Robust database with two well-structured tables (`aiosqlite`)
- Advanced logging system for easy debugging and monitoring

## 🛠️ Tech Stack

Here are the core technologies used:

- **Python** (asyncio)
- **Aiogram 3** — Telegram bot framework
- **FastAPI** — for backend and webhook support
- **APScheduler** — scheduled jobs (e.g. backups)
- **Aiofiles, Aiohttp, Aiosqlite** — async I/O
- **Uvicorn + Nginx + SSL** — production-ready deployment
- **AMO CRM API integration**
- **python-dotenv** — environment configuration
- **Rich** — beautiful CLI and logging
- … and many more libraries listed in [requirements.txt](./requirements.txt)

## 📦 Installation

```bash
# 1. Clone the repository
git clone https://github.com/Kyimatik/Onstudy-Bot.git
cd onstudy-bot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create and configure your .env file
cp .env.example .env

# 4. Run the bot
python main.py

📁 Project Structure
Onstudy-Bot/
├── dbmedia/                # Core bot logic
│   ├── callbacks.py     # Respond to all callbacks 
│   ├── config.py      # Admins id's 
├── ├── database.py    # Database ORM 
├── ├── media.py       # All media, text's etc
│   ├── start.py       # Handling start 
│   └── states.py      # FSM finite Machine , Class 
│   └── bot_instance.py # Bot and Dispatcher Initialization
│   └── payments.py # File that responsible for payment operations
├── buttons.py
├── example.env     # Environment variable template
├── main.py             # Entry point
└── requirements.txt    # Dependencies
🔒 Security & Reliability
Secure data handling via HTTPS (SSL)

Daily automatic database backups

Production-ready and scalable infrastructure

🔮 Roadmap
Web-based admin panel

Advanced CRM features

Multilingual support

Integration with more platforms

👨‍💻 Author
Developed with passion 💙
Author: [Emirlan]
[https://github.com/Kyimatik]
