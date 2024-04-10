# Library Management Studio Backend

This repository contains the backend part of the Library Management Studio project, a comprehensive system designed to facilitate efficient and intuitive management of library resources. It's built with modern web technologies and focuses on providing functionalities tailored for library staff and administrators.

## Introduction

The Library Management Studio project is developed to modernize and streamline the management processes within libraries. Utilizing web technologies, this system simplifies tasks such as managing library resources, user authentication, and the borrowing process.

## Technologies

The backend is developed using the following technologies:
- **Python 3.8+**: The core language used for backend development.
- **Flask 3.0.0**: A lightweight WSGI web application framework.
- **Flask-JWT-Extended 4.5.3**: For handling JWT-based authentication and authorization.
- **Flask-SQLAlchemy 3.1.1**: Integrating Flask applications with SQLAlchemy.
- **PostgreSQL**: As the relational database for storing all application data.
- **Alembic**: For database migrations.

Other notable technologies include Flask-Migrate for handling database migrations, PyJWT for JWT operations, and python-dotenv for managing environment variables.

## Architecture

The Library Management Studio leverages a **RESTful Architecture**, facilitating communication between the frontend and backend through well-defined HTTP methods. This structure allows for efficient, stateless interaction across the application.

### Overview

- **Frontend**: Acts as the client, sending requests to the backend via RESTful APIs. It's responsible for user interface presentation and interaction.
- **Backend**: Serves as the server, handling API requests to perform operations on the database. It manages application logic and data processing.
- **RESTful API**: Connects the frontend and backend, using HTTP methods (GET, POST, PUT, DELETE) to access and manipulate resources.


## Installation and Configuration

### System Requirements

- Python 3.8 or newer
- PostgreSQL

### Setting Up

1. **Clone the repository**:
```
  git clone https://github.com/cptn3m012/Library-Managment-Studio-Backend.git
```

2. **Navigate to the project directory**:
```
  cd Library-Managment-Studio-Backend
```

3. **Create and activate a virtual environment**:
- For Windows:
  ```
  python -m venv venv
  venv\Scripts\activate
  ```
- For Unix or MacOS:
  ```
  python3 -m venv venv
  source venv/bin/activate
  ```

4. **Install the requirements**:
```
  pip install -r requirements.txt
```

5. **Set up environment variables**:</br>
Create a `.env` file in the root directory and configure your database URI and other necessary settings as per `.env.example`.
```properties
# Database Configuration
DATABASE_URL=postgresql://[DB_USERNAME]:[DB_PASSWORD]@localhost:5432/[DB_NAME]
# Example: postgresql://postgres:password@localhost:5432/library

# Application Secrets
SECRET_KEY=[YOUR_SECRET_KEY_FOR_FLASK_APP]
JWT_SECRET_KEY=[YOUR_JWT_SECRET_KEY]
SECURITY_PASSWORD_SALT=[YOUR_SECURITY_PASSWORD_SALT]

# SMTP Configuration for Email Services
MAIL_SERVER=[YOUR_MAIL_SERVER] # e.g., smtp.gmail.com
MAIL_PORT=[YOUR_MAIL_PORT] # e.g., 465 for SSL connections
MAIL_USERNAME=[YOUR_EMAIL_ADDRESS_FOR_SMTP] # e.g., your-email@example.com
MAIL_PASSWORD=[YOUR_EMAIL_PASSWORD_OR_APP_PASSWORD_FOR_SMTP]
MAIL_USE_TLS=[True/False] # Set to False if using SSL
MAIL_USE_SSL=[True/False] # Set to True if using SSL
```

7. **Run database migrations**:
```
  flask db upgrade
```

7. **Start the Flask application**:
```
  flask run
```

## User Interface

The backend application provides support for the following key user interface components accessible through the frontend part of the Library Management System:

- **Login Page**: Enables authentication for library staff and administrators, ensuring secure access to the system's functionalities.
- **Dashboard**: A central hub for managing library resources, user accounts, and borrowing records. This includes functionalities such as adding new books, managing user accounts, and tracking book borrowings and returns.

For a hands-on experience with the User Interface, visit the frontend repository and explore the application in action. 

[Check out the User Interface here](https://github.com/cptn3m012/Library-Managment-Studio-Frontend)

By visiting the link, you can find detailed instructions on setting up the frontend environment, as well as additional insights into how the User Interface interacts with the backend to deliver a smooth library management experience.


## Security and Optimization

The backend incorporates JWT for secure authentication, data validation to protect against common vulnerabilities, and password hashing for user security.


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
