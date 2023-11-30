# Paysense

Paysense is a robust and user-friendly Flask web application that serves as a comprehensive financial management platform. Designed to streamline personal finance tracking and management, it offers a range of tools and features to assist users in efficiently managing their accounts, transactions, and expenses. With Paysense, users can create accounts, make deposits and withdrawals, and view their transaction history. The application also provides functionalities such as user registration, login, and profile management. In addition, Paysense functions as a banking application, allowing users to access their account information and offering administrators the ability to manage user accounts and view summary information about all accounts. Powered by Flask as the web framework and utilizing SQLAlchemy for seamless database operations, Paysense integrates with Flask-Login for user authentication and Flask-Mail for sending email messages. Overall, Paysense aims to provide a seamless and intuitive experience, empowering users to take control of their personal finances effectively.

## Features

- Account Management: Allows users to create, monitor, and manage multiple bank accounts within a single platform.
- Transaction Tracking: Enables users to track all their financial transactions, including deposits, withdrawals, and transfers, providing a clear overview of their financial activities.
- Expense Categorization: Helps users categorize expenses for better organization and understanding of spending habits.
- Secure Authentication: Implements secure user authentication and authorization methods for data protection.
- Email Communication with Flask-Mail: Incorporates Flask-Mail for sending email messages, enhancing user to reset their password via email.
- Profile Management: Enables users to manage their profile information, including personal details and preferences.
- User-Friendly Interface: Offers an intuitive and easy-to-use interface for effortless navigation and interaction.
- Administrator Features: Provides administrators with functionalities to manage user accounts and access summary information about all accounts.

## Technology Stack

- Backend: Python, Flask
- Database: SQLAlchemy with (SQLITE) for development or testing purpose.
- Frontend: HTML, CSS, JavaScript.

## Installation

### Requirements

- Python 3.x
- Pip

1. Clone the repository:

```bash
git clone https://github.com/AflaxCade/Paysense.git
```

2. Navigate to the project directory:

```bash
cd Paysense
```

3. Create a virtual environment:

```bash
python3 -m venv venv
```

4. Activate the virtual environment:

- For Windows:

```bash
venv\Scripts\activate
```

- For macOS and Linux:

```bash
source venv/bin/activate
```

5. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Set the environment variables:

```bash
export FLASK_APP=run.py
```

```bash
export FLASK_ENV=development
```

```bash
export SECRET_KEY=Type your own secret key
```

```bash
export MAIL_USERNAME=Your own email
```

```bash
export MAIL_PASSWORD=Your own password
```

Note: The `MAIL_USERNAME`, `MAIL_PASSWORD`, and `SECRET_KEY` are essential environment variables for the application to function properly. If you haven't set these directly in your environment, you can set them within the application itself:
In `Paysense/app/__init__.py`, Modify or change these variables like this:

```python
app.config['MAIL_USERNAME'] = 'Example@example.com'
app.config['MAIL_PASSWORD'] = 'Password'
app.config['SECRET_KEY'] = 'Yoursecretkey'
```

2. Run the application:

```bash
flask run
```

The application should now be running at `http://localhost:5000`.

## Testing

To test the application, you can visit the hosted version of the app at [Paysense on Render](https://paysense.onrender.com).

### Test User Credentials

- **Email:** guest@example.com
- **Password:** 123456

Please note that the provided test user (`guest@example.com`) does not have admin privileges.

Be patient with the link; it might load slowly the first time because free instance types tend to spin down due to inactivity.

## Contributing

If you'd like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add some feature'`).
5. Push to the branch (`git push origin feature/your-feature`).
6. Create a new Pull Request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
