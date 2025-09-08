# Npoint Uz

[![Django](https://img.shields.io/badge/Django-5.0-green?logo=django)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-REST_Framework-red?logo=django)](https://www.django-rest-framework.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-4-blueviolet?logo=bootstrap)](https://getbootstrap.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://www.python.org/)

**Npoint Uz** is a modern platform that lets users **create, manage, and share JSON documents** with ready-to-use API endpoints.  
It is built with **Django + Django REST Framework**, styled with **Bootstrap 4**, and features clean UI/UX.

---

## 📸 Screenshots

### Dashboard Statistics
![Dashboard Stats](./docs/screenshots/dashboard.png)

### JSON Document Cards
![JSON Grid](./docs/screenshots/json_grid.png)

### API Example
![API Endpoint](./docs/screenshots/api_example.png)

---

## ✨ Features

- 🔑 **Authentication**
  - Register / Login / Logout  
  - Profile with avatar  
  - Secure password reset via email  

- 📂 **JSON Management**
  - Create, edit, delete JSON docs  
  - Public/Private toggle  
  - Auto-generated API endpoints  

- 🌐 **API**
  - Token-based authentication  
  - Public APIs (open access with token)  
  - Private APIs (restricted to owner)  

- 📊 **Statistics**
  - Total users  
  - JSON files count  
  - API calls tracked in real time  

- 🎨 **UI**
  - Responsive design (Bootstrap 4)  
  - Turquoise/green theme (`#20c997 / #38d9a9`)  
  - Clean modern typography (Poppins / Inter)  

---

## 🚀 Tech Stack

- **Backend:** Django 5, Django REST Framework  
- **Frontend:** Bootstrap 4, custom CSS  
- **Database:** SQLite (dev) / PostgreSQL (prod)  
- **Auth:** TokenAuthentication, Session auth  
- **Other:** Pillow (images), Django Messages  

---

## 📦 Installation

```bash
# Clone repo
git clone https://github.com/your-username/npoint-uz.git
cd npoint-uz

# Setup venv
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Install deps
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create admin
python manage.py createsuperuser

# Start server
python manage.py runserver
##🔑 API Usage
Authentication
Authorization: Token <your_api_token>

#Endpoints

GET /api/public/json/ → List public JSON docs

GET /api/public/json/<username>/<slug>/<id>/ → Get JSON doc

POST /api/public/json/ → Create new JSON doc (auth required)

# Example (Python)
import requests

url = "https://npoint.uz/api/johndoe/todolist/13/"
headers = {"Authorization": "Token YOUR_API_TOKEN"}

res = requests.get(url, headers=headers)
print(res.json())

##📊 Statistics

The system tracks:

Total Users

Total JSON Files

API Calls (incremented per request)

Shown in index.html and main.html via a shared _stats.html template.

## ⚙️ Project Structure
npoint_project/
├── npoint_app/
│   ├── models.py
│   ├── views.py
│   ├── api.py
│   ├── serializers.py
│   ├── templates/npoint_app/
│   └── static/npoint_app/
├── docs/screenshots/
│   ├── dashboard.png
│   ├── json_grid.png
│   └── api_example.png
└── manage.py

## 🔒 Privacy Policy

By using Npoint Uz, you agree that:

JSON content belongs to you

Public APIs are open access

Tokens are your responsibility

See Privacy Policy
 for details

## 🤝 Contributing

We welcome contributions from the community!  

To contribute:  
1. **Fork** the repository  
2. **Create a branch** for your feature or bugfix  
   ```bash
   git checkout -b feature/your-feature-name

3. **Commit your changes** with clear messages
    ```bash
    git commit -m "Add: new feature description"


4. **Push** to your fork
    ```bash
    git push origin feature/your-feature-name

5. **Open a Pull Request** describing your changes

- **Please follow best practices:**

- **Keep code clean and readable

- **Add comments where necessary**

- **Update documentation if you add/change features**

## 📧 Contact

🌐 Website: https://npoint.uz

📧 Email: [your-email@example.com
]

## 📜 License