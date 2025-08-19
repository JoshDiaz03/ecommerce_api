E-Commerce API

Overview

This project is a RESTful API for an e-commerce platform built using Flask, a lightweight Python web framework. It provides endpoints to manage users, products, and orders, with a MySQL database backend using SQLAlchemy for ORM and Marshmallow for data serialization and validation. The API supports CRUD operations for users and products, as well as order creation and management, including adding/removing products from orders.

Features





User Management: Create, read, update, and delete (CRUD) user information (name, email, address).



Product Management: CRUD operations for products (name, price).



Order Management: Create orders, associate them with users, and manage products in orders.



Database: MySQL database with relationships (many-to-one between users and orders, many-to-many between orders and products).



Data Validation: Input validation using Marshmallow schemas.



RESTful Endpoints: JSON-based API with appropriate HTTP status codes.

Technologies Used





Python 3.x



Flask: Web framework for building the API.



SQLAlchemy: ORM for database operations.



Flask-SQLAlchemy: Flask extension for SQLAlchemy integration.



Marshmallow: Serialization and deserialization of data with validation.



Flask-Marshmallow: Integration of Marshmallow with Flask.



MySQL: Relational database for storing users, products, and orders.



mysql-connector-python: MySQL driver for Python.

Prerequisites





Python 3.8 or higher



MySQL server (e.g., MySQL Community Server)



pip (Python package manager)



Virtual environment (recommended)