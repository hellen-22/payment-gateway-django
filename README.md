# PAYMENT GATEWAYS
Backend API Payment Gateways - Paystack

### To Run The Project Locally.
- Clone the repository and navigate to the folder with the project.
  ```sql
    git clone https://github.com/hellen-22/payment-gateway-django.git
    cd payment-gateway-django/
  ```
- Create a virtual environment and activate it:
  ```sql
    For windows.
    python -m venv venv
    venv/Scripts/activate

    Others.
    python3 -m venv venv
    source venv/bin/activate
  ```
- Install the required packages/libraries:
  ```sql
    pip3 install -r requirements.txt
  ```
- Create a .env file within the project folder(payment-gateway-django) and use the env variables in .env.example to edit the file and add the respective environment variables values.

- Set up the database by running the migrations
  ```sql
    python3 manage.py migrate
  ```
- You can now run the project and access it using [127.0.0.0:8000](http://127.0.0.1:8000/) locally.
  ```sql
    python3 manage.py runserver
  ```
- The documentation is on [127.0.0.0:8000](http://127.0.0.1:8000/)
