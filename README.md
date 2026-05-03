# 🏏 Cricket Vision Intelligence System

> AI-powered cricket analytics system that understands gameplay using computer vision and AI.

---

## 🚀 Overview

Cricket Vision Intelligence System is designed to analyze cricket matches beyond traditional statistics. Using **Computer Vision + AI (Gemini API)**, it detects shots, classifies deliveries, and generates intelligent insights from match visuals.

---

## 🎯 Problem Statement

Traditional cricket analytics only provide:

* Runs scored
* Ball speed
* Strike rate

They fail to capture:

* Shot type played
* Type of delivery bowled
* Context behind gameplay

---

## 💡 Solution

This system processes cricket images and match visuals to generate:

* 🎯 Shot classification (cover drive, pull, etc.)
* 🎯 Ball type detection (yorker, bouncer, swing)
* 🧠 AI-generated insights using Gemini API
* 📊 Context-aware match analysis

---

## 📁 Dataset (Images)

The system uses cricket images stored locally for analysis.

### 📍 Local Dataset Path:

```id="datasetpath1"
C:\Users\Parth\.gemini\antigravity\gdgps1\photos
```

### ⚠️ Important Notes:

* This path is **local to your system** and will NOT work on other machines or deployments.
* For portability, move images inside the project directory like:

```id="datasetpath2"
project_root/
└── photos/
```

Then update your code:

```python id="datasetpath3"
image_folder = "photos/"
```

---

## ⚙️ Tech Stack

* **Backend:** Python
* **AI:** Gemini API
* **Computer Vision:** OpenCV
* **Frontend:** HTML, CSS, JavaScript
* **Libraries:** NumPy, Pandas

---

## 📂 Project Structure

```id="structure1"
CRICKET_VISION_INTELL_SYSTEM_GDG/
│
├── agents/              # AI logic
├── static/              # CSS, JS, assets
├── templates/           # HTML files
├── photos/              # Image dataset (recommended location)
├── main.py              # Main application
├── requirements.txt     # Dependencies
├── .env                 # API keys (ignored)
└── README.md
```

---

## 🔧 Installation & Setup

### 1️⃣ Clone Repository

```bash id="install1"
git clone https://github.com/parth-khera/CRICKET_VISION_INTELL_SYSTEM_GDG.git
cd CRICKET_VISION_INTELL_SYSTEM_GDG
```

### 2️⃣ Create Virtual Environment

```bash id="install2"
python -m venv venv
venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```bash id="install3"
pip install -r requirements.txt
```

### 4️⃣ Setup Environment Variables

Create `.env` file:

```id="install4"
GEMINI_API_KEY=your_api_key_here
```

---

### 5️⃣ Run the Project

```bash id="install5"
python main.py
```

---

## 📸 Features

* 🎯 Shot detection using computer vision
* ⚡ Real-time match understanding
* 🧠 AI-powered insights generation
* 🖼️ Image-based cricket analysis
* 📊 Advanced analytics beyond scoreboards

---

## 🔮 Future Improvements

* 📡 Live match video processing
* 📊 Player heatmaps
* 🤖 Predictive analytics
* 🌐 Cloud deployment support

---

## 🧪 Use Cases

* Sports analytics platforms
* Coaching tools
* Broadcasting enhancements
* AI commentary systems

---

## 🤝 Team

* **Parth Khera**
* Sourabh
* Ashutosh
* Deepanshu

---

## 📜 License

MIT License

---

## ⭐ Support

If you like this project:

* ⭐ Star the repo
* 🍴 Fork it
* 🤝 Contribute

---

> ⚡ "Turning cricket visuals into intelligence."
