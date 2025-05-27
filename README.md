# Ticket Booking Chatbot with Image Classifier & WhatsApp Integration

This Flask-based project integrates chatbot-driven ticket booking, image classification, and WhatsApp messaging using Selenium. It includes QR code ticket generation and a chatbot interface with local LLM backend support.

---

## 🔧 Features

- 🤖 Chatbot with contextual flow for booking, viewing, and cancelling tickets
- 📅 Ticket ID generation with visiting date storage
- 📷 Image classification using a trained Keras model
- 📤 WhatsApp messaging (with ticket & QR code image) via Selenium
- 🔍 Ticket verification system
- 🧠 LLM Integration (via LM Studio or OpenAI compatible API)
- 📄 Data stored in local JSON file for persistence
- 🌐 Web interface using Flask and HTML templates

---

## 📁 Folder Structure

```
├── app.py                    # Main Flask application
├── class_indices.json        # Label map for classifier
├── image_classifier_model.h5 # Trained model file
├── database.txt              # Stores user & ticket info
├── static/
│   └── qr_codes/             # Auto-generated QR codes
├── templates/
│   ├── index.html            # Chat interface
│   └── ticket.html           # Ticket display page
```

---

## ⚙️ Setup Instructions

1. **Clone the repository**

   ```bash
   git clone <your-repo-url>
   cd chatbot
   ```

2. **Install dependencies**

   ```bash
   pip install flask keras numpy pillow selenium qrcode
   ```

3. **Ensure Chromedriver is installed and compatible with your Chrome version.**

4. **Run LM Studio (or any OpenAI-compatible API) locally on port `1000`**

5. **Start the Flask App**

   ```bash
   python app.py
   ```

6. **Navigate to** [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 💬 WhatsApp Integration (Manual Login)

- Make sure to have Chrome installed.
- When sending a message for the first time, scan the WhatsApp Web QR manually in the browser pop-up.
- Session will persist using Chrome user profile (`Chrome/User Data`).

---

## 🧠 LLM Integration

- LM Studio or OpenAI-compatible endpoint must run on `http://localhost:1000`
- Works with requests to `/v1/chat/completions`

---

## 📷 Image Prediction

- Endpoint: `/predict` (POST)
- Upload image file
- Returns predicted class and description if confidence > 90%

---

## 📝 To-Do

- Add user authentication
- Migrate database to SQLite or MongoDB
- Deploy on cloud (Render, Heroku, etc.)

---

## 🤝 Credits

- [Keras](https://keras.io)
- [Flask](https://flask.palletsprojects.com/)
- [Selenium](https://www.selenium.dev/)
- [LM Studio](https://lmstudio.ai)
- [WhatsApp Web](https://web.whatsapp.com)

---
