# 🔷 Rix Solve — Python/Flask Video Platform

> Learn. Code. Solve. Grow. | Math. Tech. Versatility.

---

## 📁 Project Structure

```
rixsolve/
├── app.py              ← Flask backend (API + routes)
├── requirements.txt    ← Python packages
├── Procfile            ← For deployment (Railway/Render/Heroku)
├── templates/
│   └── index.html      ← Full frontend (HTML/CSS/JS)
└── static/
    └── uploads/        ← Videos saved here (auto-created)
```

---

## ⚙️ Run Locally (on your PC)

### 1. Make sure Python is installed
Download from https://python.org (version 3.9 or higher)

### 2. Install packages
Open a terminal in the project folder and run:
```bash
pip install -r requirements.txt
```

### 3. Start the server
```bash
python app.py
```

### 4. Open your browser
Go to: **http://localhost:5000**

That's it! ✅

---

## 🌐 Deploy Free Online (Railway)

1. Create free account at https://railway.app
2. Click "New Project" → "Deploy from GitHub"
3. Upload your project to GitHub first, then connect it
4. Railway auto-detects the Procfile and deploys

OR use the Railway CLI:
```bash
pip install railway
railway login
railway init
railway up
```

---

## ✏️ Update Your Info

Open `templates/index.html` and search for these lines to update:

| What to change | Search for |
|----------------|-----------|
| Instagram handle | `@rixsolve` (Instagram) |
| WhatsApp number | `254700000000` |
| YouTube channel | `@rixsolve` (YouTube) |
| Your bio text | "I'm Rix — a tech educator..." |

---

## 📡 API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/videos` | List all videos |
| POST | `/api/videos/upload` | Upload a video |
| DELETE | `/api/videos/<id>` | Delete a video |
| GET | `/api/videos/<id>/comments` | Get comments |
| POST | `/api/videos/<id>/comments` | Add a comment |
| GET | `/uploads/<filename>` | Stream/download video |

---

Built with ❤️ for Rix Solve.
