<div align="center">

# 🎬 Video Streaming Server



</div>

---

## About

A console-based video streaming application built in Python using **TCP sockets**. Users can sign up, log in, browse a video dashboard, and stream video content over a socket connection. Video data is fetched and displayed from a **Supabase** database.

---

## Features

- 🔐 User Login & Signup
- 🎛️ Video Dashboard
- 📡 Socket-based Client & Server
- 🎥 Video Streaming over TCP
- 🗄️ Supabase Integration

---

## Getting Started

**1. Clone the repo**
```bash
git clone https://github.com/AmitPundekar16/vide-streaming-server.git
cd vide-streaming-server
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Set up `.env`**
```env
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-anon-key
```

**4. Run the server & client**
```bash
python server.py
python client.py
```

---

## Tech Stack

- **Python** — Core language
- **Sockets** — TCP networking
- **Supabase** — Database & Auth

---

<div align="center">
Made with 🐍 Python
</div>
