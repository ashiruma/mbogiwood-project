Mbogiwood Productions
Empowering African Narratives.

Mbogiwood is a modern, scalable web platform designed to be the definitive home for Kenyan and African cinema. It serves as a dual-sided marketplace that connects visionary filmmakers with a passionate audience, providing creators with the tools to monetize their content and viewers with access to a rich library of authentic stories.

This is more than just a streaming service; it is a full-stack digital production house built on a robust, secure, and professional architecture.

Core Features & Architecture
This project is built on a series of well-defined, decoupled systems designed for scalability and maintainability.

Identity & Access Management (users app): A secure user lifecycle system built on an email-based identity model. It includes mandatory email verification, role-based access (Viewer vs. Creator), and a complete governance workflow for creator onboarding.

Content Ingestion Pipeline (videos app): A professional-grade, cloud-native upload system. It uses a "Direct-to-Cloud" architecture with pre-signed URLs to handle large video files securely and efficiently, bypassing the application server to prevent bottlenecks.

Payment & Subscription Engine (payments app): A resilient payment gateway system, architected first for Kenya's primary payment method (M-Pesa via Daraja), with a data model designed to easily accommodate future providers like Stripe. The system is designed with idempotency and data integrity checks to handle real-world transaction failures.

Creator Economy (payouts logic): A sustainable and fair "Creator Pool" revenue-sharing model. Payouts are directly tied to monthly subscription revenue and viewership metrics, ensuring the platform's financial health. An automated management command handles the entire end-of-month payout calculation.

Governance & Auditing: An immutable CreatorReviewLog provides a permanent audit trail for all administrative actions related to creator approvals and rejections, ensuring accountability.

Technology Stack
Backend: Python 3, Django, Django REST Framework

Frontend: HTML5, Tailwind CSS (via CDN for prototyping), Vanilla JavaScript

Database: PostgreSQL (recommended for production), SQLite (for local development)

Deployment (Recommended): Docker, Gunicorn, Nginx

Key Python Packages: See requirements.txt

Project Structure
The project follows a standard, modular Django structure:

mbogiwood-project/
├── core/                  # Main project settings & config
├── users/                 # User management, auth, creator onboarding
├── videos/                # Video content models, upload API
├── payments/              # Payment models, Daraja integration
├── static/                # Shared CSS, JS, and images
└── templates/             # HTML files for the frontend

Local Development Setup
Follow these steps to get the project running on your local machine.

1. Prerequisites
Python 3.8+

Pip (Python package installer)

Git

2. Clone the Repository
git clone [https://github.com/ashiruma/mbogiwood.git](https://github.com/ashiruma/mbogiwood.git)
cd mbogiwood

3. Set Up a Virtual Environment
It is highly recommended to use a virtual environment to manage project dependencies.

# Create the virtual environment
python -m venv venv

# Activate it
# On Windows:
# venv\Scripts\activate
# On macOS/Linux:
# source venv/bin/activate

4. Install Dependencies
Install all required packages from the requirements.txt file.

pip install -r requirements.txt

5. Configure Environment Variables
This project uses a .env file to manage secret keys and other environment-specific settings.

Create a file named .env in the root of the project.

Add the following content to it. Generate a new, strong secret key for your project.

# .env
SECRET_KEY='your-strong-django-secret-key-here'
DEBUG=True
DATABASE_URL='sqlite:///db.sqlite3'

You will also need to update core/settings.py to read these variables.

6. Run Database Migrations
Apply the database schema we have designed to your local database.

python manage.py makemigrations
python manage.py migrate

7. Create a Superuser
This creates an administrator account that can access the Django Admin interface.

python manage.py createsuperuser

Follow the prompts to set up your email and password.

8. Run the Development Server
You are now ready to run the project!

python manage.py runserver

The application will be available at http://127.0.0.1:8000/. You can access the admin panel at http://127.0.0.1:8000/admin/.

Architectural Notes
Email-Based Authentication: The system uses email as the primary identifier for users, which is a secure and user-friendly standard. There is no username field.

Creator Onboarding: New creators sign up with is_creator=True but are placed in a pending status. They must be manually approved by an admin via the Django Admin interface before they can upload content. All approval/rejection actions are logged for accountability.

Direct-to-Cloud Uploads: The video upload flow is designed to be highly scalable. The frontend will request a secure URL from the backend, upload the file directly
