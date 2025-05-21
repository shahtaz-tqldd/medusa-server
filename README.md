# Medusa Backend Server

The server is developed with **Python, Django**, and **Django REST Framework**. This backend serves as an **authentication service** and manages **projects, blogs, skills**, and provides interaction with an ai **chatbot**.

---

## 📚 Features

* **Authentication**

  * User Registration
  * User Login
  * Profile Retrieval
  * Password Reset via Email OTP

* **Project Management**

  * Create, Update, Delete, and Retrieve Projects

* **Services**

  * Create, Update, Delete, and Retrieve Services

* **Skills**

  * Create, Update, Delete, and Retrieve Skills

* **Blogs**

  * Create, Update, Delete, and Retrieve Blogs
  * Manage Blog Categories and Tags

* **Chatbot Interaction**

  * APIs for chatbot integration

---

## 🖥️ Local Development Setup

### 1️⃣ Create Virtual Environment

```bash
python -m venv env
```

### 2️⃣ Activate Virtual Environment

* **On Windows**

```bash
cd env\Scripts\activate
```

* **On Linux / macOS**

```bash
source env/bin/activate
```

### 3️⃣ Apply Migrations

```bash
python manage.py migrate
```

### 4️⃣ Configure Environment Variables

Create or update a `.env` file in the project root directory with your **database settings**, **email configurations**, and other environment-specific variables.

### 5️⃣ Run the Development Server

```bash
python manage.py runserver
```

---

## 🐳 Run with Docker

### 1️⃣ Configure Environment Variables

Make sure your `.env` file is properly configured.

### 2️⃣ Run Docker

* **On Linux / macOS**

```bash
bash start_app.sh
```

> 📌 Ensure Docker is installed and running on your system.

* **On Windows**

```bash
start_app.bat
```

> 📌 Make sure Docker Desktop is running.

---

## 📬 API Documentation

Explore the full API documentation via Postman:

👉 [Postman API Docs](https://documenter.getpostman.com/view/36267101/2sB2qZDh2w)

---

## ⚙️ Tech Stack

* **Python 3**
* **Django**
* **Django REST Framework**
* **PostgreSQL (recommended)**
* **Docker**
* **Docker Compose**

---

## 📌 Notes

* Make sure to set your **necessary credentials** for the `.env` using reference from `.env.example` file.
* Docker must be installed and running to use Docker deployment.
* Postman collection link is available above for API testing.
