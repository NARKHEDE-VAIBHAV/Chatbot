from flask import Flask, request, jsonify, render_template, url_for
from keras.models import load_model
from keras.preprocessing import image
from PIL import Image
import numpy as np
import json
import os
import datetime
import random
import requests
import qrcode
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

app = Flask(__name__)

qr_data = f"https://<url here>/ticket={ticket_id}"
EMAIL_SENDER = "email@gmail.com"
EMAIL_APP_PASSWORD = "<securet key from google app password>"

model_path = r'image_classifier_model.h5'
class_indices_path = r'class_indices.json'
model = load_model(model_path)

with open(class_indices_path, 'r') as f:
    class_indices = json.load(f)
class_labels = {v: k for k, v in class_indices.items()}

def prepare_image(img_path):
    img = Image.open(img_path)
    img = img.resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

DATABASE_FILE = r'database.txt'
users = {}
tickets = {}



def send_email_with_qr(recipient, ticket_id, visiting_date, name, age):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = recipient
    msg['Subject'] = f"Your Ticket ID: {ticket_id}"

    body = f"Hello {name},\n\nYour ticket for {visiting_date} has been booked for {age} person(s).\nTicket ID: {ticket_id}\n\nAttached is your QR code for verification."
    msg.attach(MIMEText(body, 'plain'))

    qr_path = f"static/qr_codes/{ticket_id}.png"
    with open(qr_path, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={ticket_id}.png')
        msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(EMAIL_SENDER, EMAIL_APP_PASSWORD)
    server.send_message(msg)
    server.quit()

def load_data():
    global users, tickets
    if os.path.exists(DATABASE_FILE):
        try:
            with open(DATABASE_FILE, 'r') as file:
                data = json.load(file)
                users = data.get('users', {})
                tickets = data.get('tickets', {})
        except json.JSONDecodeError:
            users, tickets = {}, {}
    else:
        users, tickets = {}, {}

def save_data():
    with open(DATABASE_FILE, 'w') as file:
        json.dump({'users': users, 'tickets': tickets}, file)

def generate_ticket_id():
    return str(random.randint(1000000000, 9999999999))

def generate_qr_code(ticket_id):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    qr_path = f"static/qr_codes/{ticket_id}.png"
    os.makedirs(os.path.dirname(qr_path), exist_ok=True)
    img.save(qr_path)
    return qr_path

def add_user(phone, name, age, visiting_date, email):
    ticket_id = generate_ticket_id()
    users[phone] = {'name': name, 'age': age, 'email': email}
    tickets[ticket_id] = {'phone': phone, 'visiting_date': visiting_date}
    save_data()
    qr_path = generate_qr_code(ticket_id)
    send_email_with_qr(email, ticket_id, visiting_date, name, age)
    return ticket_id, qr_path

def get_user_by_phone(phone):
    return users.get(phone)

def get_ticket_by_id(ticket_id):
    return tickets.get(ticket_id)

def get_tickets_by_phone(phone):
    return {tid: info for tid, info in tickets.items() if info['phone'] == phone}

def cancel_ticket(ticket_id):
    if ticket_id in tickets:
        del tickets[ticket_id]
        save_data()
        return True
    return False

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message'].strip()
    user_data = request.json.get('user_data', {})

    if 'phone' not in user_data:
        if user_message.isdigit() and len(user_message) == 10 and user_message[0] in '6789':
            phone = user_message
            user_data['phone'] = phone
            user_record = get_user_by_phone(phone)
            if user_record:
                response = f"Welcome back, {user_record['name']}! How can I assist you today?"
                user_data['name'] = user_record['name']
            else:
                response = "I don't have your details. Please provide your name."
                user_data['state'] = 'awaiting_name'
        else:
            response = "Please enter a valid 10-digit Indian phone number."
        return jsonify({'reply': response, 'user_data': user_data})

    if "book a ticket" in user_message.lower():
        user_record = get_user_by_phone(user_data['phone'])
        if user_record and user_record.get('email'):
            user_data['email'] = user_record['email']
            response = "Please provide number of people who are visiting."
            user_data['state'] = 'awaiting_age'
        else:
            response = "Please provide your email address."
            user_data['state'] = 'awaiting_email'
        return jsonify({'reply': response, 'user_data': user_data})

    elif "cancel my ticket" in user_message.lower():
        tickets_to_cancel = get_tickets_by_phone(user_data['phone'])
        if tickets_to_cancel:
            response = "Please provide the ticket ID you wish to cancel:\n" + "\n".join(tickets_to_cancel.keys())
            user_data['state'] = 'awaiting_cancel_id'
        else:
            response = "No tickets found for your phone number."
        return jsonify({'reply': response, 'user_data': user_data})

    elif "view my ticket" in user_message.lower():
        tickets_to_view = get_tickets_by_phone(user_data['phone'])
        if tickets_to_view:
            response = "Your tickets:<br>" + "<br>".join(
                f"Ticket ID: {tid}, Visiting Date: {info['visiting_date']}.<br><img src='static/qr_codes/{tid}.png' alt='qr' class='bot-image'>"
                for tid, info in tickets_to_view.items()
            )
        else:
            response = "No tickets found for your phone number."
        return jsonify({'reply': response, 'user_data': user_data})

    if user_data.get('state') == 'awaiting_name':
        user_data['name'] = user_message
        response = "Please provide your email address."
        user_data['state'] = 'awaiting_email'
        return jsonify({'reply': response, 'user_data': user_data})

    if user_data.get('state') == 'awaiting_email':
        if user_message.endswith("@gmail.com"):
            user_data['email'] = user_message
            response = "Please provide number of people who are visiting."
            user_data['state'] = 'awaiting_age'
        else:
            response = "Please enter a valid Gmail."
        return jsonify({'reply': response, 'user_data': user_data})

    if user_data.get('state') == 'awaiting_age':
        if user_message.isdigit() and 0 < int(user_message) < 150:
            user_data['age'] = int(user_message)
            response = "Please select your desired visiting date using the date picker."
            user_data['state'] = 'awaiting_date'
        else:
            response = "Please enter a number."
        return jsonify({'reply': response, 'user_data': user_data})

    if user_data.get('state') == 'awaiting_date':
        try:
            visiting_date = datetime.datetime.strptime(user_message, "%Y-%m-%d").date()
            user_data['visiting_date'] = str(visiting_date)
            existing_tickets = get_tickets_by_phone(user_data['phone'])
            if any(ticket['visiting_date'] == user_data['visiting_date'] for ticket in existing_tickets.values()):
                response = f"You already have a ticket for {visiting_date}."
            else:
                ticket_id, qr_path = add_user(user_data['phone'], user_data['name'], user_data['age'], user_data['visiting_date'], user_data['email'])
                response = f"Thank you, {user_data['name']}. Your ticket has been booked for date {visiting_date} for total {user_data['age']}! Your ticket ID is {ticket_id}.<br><img src='static/qr_codes/{ticket_id}.png' alt='qr' class='bot-image'>"
        except ValueError:
            response = "Please enter a valid date in the format YYYY-MM-DD."
        return jsonify({'reply': response, 'user_data': user_data})

    if user_data.get('state') == 'awaiting_cancel_id':
        ticket_id = user_message
        canceled = cancel_ticket(ticket_id)
        response = f"Your ticket with ID {ticket_id} has been canceled." if canceled else "No ticket found with that ticket ID."
        user_data['state'] = None
        return jsonify({'reply': response, 'user_data': user_data})

    if "verify ticket" in user_message.lower():
        response = "Please provide your ticket ID to verify."
        user_data['state'] = 'awaiting_ticket_verification'
        return jsonify({'reply': response, 'user_data': user_data})

    if user_data.get('state') == 'awaiting_ticket_verification':
        ticket_id = user_message.strip()
        ticket_info = get_ticket_by_id(ticket_id)
        if ticket_info:
            user_info = get_user_by_phone(ticket_info['phone'])
            response = f"Ticket Verified!\nName: {user_info['name']}\nNumber of People: {user_info['age']}\nEmail: {user_info['email']}\nVisiting Date: {ticket_info['visiting_date']}"
        else:
            response = "Sorry, we couldn't find a valid ticket with that ID."
        user_data['state'] = None
        return jsonify({'reply': response, 'user_data': user_data})

    try:
        lm_response = requests.post(
            'http://localhost:1000/v1/chat/completions',
            json={'messages': [{'role': 'user', 'content': user_message}]}
        )
        lm_response.raise_for_status()
        lm_reply = lm_response.json().get('choices')[0]['message']['content']
    except requests.exceptions.RequestException as e:
        lm_reply = f"I'm having trouble connecting to the language model service. Error: {str(e)}"

    return jsonify({'reply': lm_reply, 'user_data': user_data})

@app.route('/ticket=<ticket_id>')
def view_ticket(ticket_id):
    ticket_info = get_ticket_by_id(ticket_id)
    if ticket_info:
        user_info = get_user_by_phone(ticket_info['phone'])
        return render_template('ticket.html', ticket_id=ticket_id, user_info=user_info, ticket_info=ticket_info)
    else:
        return "Ticket not found", 404

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    
    img_path = 'uploaded_image.jpg'
    file.save(img_path)  
    img_array = prepare_image(img_path)

    prediction = model.predict(img_array)
    class_idx = np.argmax(prediction)
    class_label = class_labels[class_idx]
    confidence = float(prediction[0][class_idx])
    
    # Check if confidence is greater than 90%
    if confidence > 0.90:
        try:
            lm_response = requests.post(
                'http://localhost:1000/v1/chat/completions',
                json={'messages': [{'role': 'user', 'content': f"Can you tell me about {class_label}?"}]}
            )
            lm_response.raise_for_status()  
            lm_reply = lm_response.json().get('choices')[0]['message']['content']
        except requests.exceptions.RequestException as e:
            lm_reply = f"I'm having trouble connecting to the language model service. Error: {str(e)}"
        if confidence > 0.90:
            return jsonify({'class': class_label, 'confidence': confidence, 'description': lm_reply})
        else:
            return jsonify({'message': "Sorry, no data found", 'confidence': confidence})
    else:
        return jsonify({'message': "Sorry, no data found", 'confidence': confidence})

if __name__ == '__main__':
    load_data()
    app.run(debug=True, port=5000)
