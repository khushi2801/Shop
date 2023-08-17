# Shop
Shop is an e-commerce platform for clothing, built on the Django Web Framework.

## Features

**Common**
- Customer and Merchant Login/Register
- Profile Management

**Merchant Site**
- Product Add/Delete/Update
- Sales Metrics

**Customer Site**
- Shopping Cart
- Coupon/Discount Options
- Order History and Management

## Upcoming Features
- Payment Options
- Product Category Filter/Search

## Installation 
Clone repository
```
git clone https://github.com/khushi2801/Shop.git
```
Create virtual environment and install packages
```
cd Shop
python3 -m venv shop_env
source shop_env/bin/activate
pip install -r requirements.txt
```
Migrate database
```
python3 manage.py makemigrations
python3 manage.py migrate
```
Create superuser
```
python3 manage.py createsuperuser
```
Start server
```
python3 manage.py runserver
```
