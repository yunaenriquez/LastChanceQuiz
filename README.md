Project Name:IkotIkotLang

Installation Instructions
1. Clone the Project
git clone https://github.com/<your-username>/<your-repo-name>.git
cd final

2. Set Up a Virtual Environment
python -m venv .venv
.venv\Scripts\activate

3. Install Dependencies
pip install -r requirements.txt
pip freeze > requirements.txt

4. Apply Database Migrations
python manage.py makemigrations
python manage.py migrate

5. Create an Admin Account

This account will manage users and rides.

python manage.py createsuperuser


You will be asked to provide:

Username:

Email:

Password:

6. Launch the Development Server
python manage.py runserver

Purpose: 
This project is a booking system that helps customers find riders who can take them to their desired destination. Customers can easily request a ride, and riders can accept the booking if they agree with the price offered. The system keeps track of the entire ride by updating the status and recording each important action along the way.

The goal of this platform is to make ride management simple and organized for everyone involved. It handles trip tracking, balance updates, and smooth communication across three different user roles:

• Customers who create and manage their ride requests
• Riders who accept bookings and complete rides
• Staff who oversee all operations within the system

This system ensures transparency of each ride’s progress, while automating distance tracking, balance updates, and event logs to provide a smooth experience for all users involved.


Fixes:
-Login and registration features are now working for existing and new users

-Customer dashboard shows account balance and ride information

-Core dashboard sections added: Active Rides, Request a Ride, Ride History, and Profile Page

-Ride request form now includes pickup and destination options along with a minimum fare input

To be fixed:
-Correct role detection and redirecting users to the appropriate dashboard (Customer, Rider, Staff)

-Ensuring all sidebar navigation links work based on the user’s role

-Completing the booking workflow and ride acceptance process
