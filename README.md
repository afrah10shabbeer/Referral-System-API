**FastAPI Referral System**
This FastAPI application provides a referral system with endpoints for user registration, authentication, and retrieving user details.

**Endpoints:**
POST /register/

Registers a new user with the provided user data.
Endpoint URL: /register/
Method: POST
Request Body: JSON containing user details including name, email, password, and referral code.
Response: Returns a message confirming successful registration along with a unique user ID.

**POST /Authorisation**
Authenticates a user and generates an access token for authorization.
Endpoint URL: /Authorisation
Method: POST
Request Body: Form data containing the username (email) and password.
Response: Returns an access token for authorization.

**GET /users_details/**
Retrieves details of a user by their user ID.
Endpoint URL: /users_details/
Method: GET
Query Parameters: user_id (integer) - ID of the user whose details are to be retrieved.
Response: Returns details of the specified user including name, email, referral code, and timestamp.

**GET /referral_details/**
Retrieves details of users who have utilized a specific referral code.
Endpoint URL: /referral_details/
Method: GET
Query Parameters: referral_code (string) - Referral code for which user details are to be retrieved.
Response: Returns a list of user details including name, email, referral code, and timestamp.

**Security:**
User passwords are securely hashed before storing them in the database.
Access tokens are generated using JWT (JSON Web Tokens) for secure authentication and authorization.

**Backend Database:**
MySQL database is used as the backend database for storing user information.
Database configuration is provided in the db_config dictionary within the application.
Database connection pooling is implemented for efficient management and reuse of database connections.

**Dependencies:**
FastAPI: A modern, fast (high-performance) web framework for building APIs with Python.
Pydantic: Data validation and settings management using Python type annotations.
Jose: JavaScript Object Signing and Encryption library for JSON Web Tokens (JWT).
Passlib: Secure password hashing and authentication.
MySQL Connector: Python driver for connecting to MySQL databases.
