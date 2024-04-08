# Import necessary modules
import mysql.connector
import mysql.connector.pooling
from typing import List, Optional
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# from database import get_mysql_db
db_config = {
    'user':'root',
    'host':'localhost',
    'password':'open',
    'database':'referral_db'
}

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "06d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1

class UserDetails(BaseModel):
    name: str
    email: str
    referral_code: str
    timestamp:Optional[datetime] = None

class UserModel(UserDetails):
    id: Optional[int] = None
    password: str

# A model for representing authentication tokens, consisting of an access_token (a unique identifier granting access) and a token_type (specifying the type of token, often "bearer").
class Token(BaseModel):
    access_token:str
    token_type:str

class TokenData(BaseModel):
    email: str | None = None

pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")
outh2_scheme = OAuth2PasswordBearer(tokenUrl="Authorisation")

app = FastAPI()

# pool efficiently manages and reuses database connections, and avoids the creation of new connection every req
db_connection_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name = "my_pool",**db_config)

# Verifies plain password to hashed password
def verify_password(plain_password, password):
    return pwd_context.verify(plain_password, password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user_by_email(user_email: str):
    try:
        connection = db_connection_pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        sql_query = "SELECT * FROM users_table WHERE email = %s"
        cursor.execute(sql_query, (user_email,))

        # Fetch one row (if exists)
        result = cursor.fetchone()
        if result:
            return UserModel(**result)

    except mysql.connector.Error as e:
        print(f"Error: {e}")
        return None
    finally:
        if connection.is_connected():
            connection.close()
            print("MySQl connection is closed")

def get_user_by_id(user_id: int):
    try:
        connection = db_connection_pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        sql_query = "SELECT * FROM users_table WHERE id = %s"
        cursor.execute(sql_query, (user_id,))

        # Fetch one row (if exists)
        result = cursor.fetchone()
        if result:
            return UserModel(**result)

    except mysql.connector.Error as e:
        print(f"Error: {e}")
        return None
    finally:
        if connection.is_connected():
            connection.close()
            print("MySQl connection is closed")

def get_users_by_referral_code(user_referral_code: str):
    try:
        connection = db_connection_pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        sql_query = "SELECT * FROM users_table WHERE referral_code = %s"
        cursor.execute(sql_query, (user_referral_code,))

        # Fetch one row (if exists)
        result = cursor.fetchall()
        # Construct a list of UserInDB objects from the result
        users = []
        for result in result:
            users.append(UserModel(**result))

        if users:
            return users
        
    except mysql.connector.Error as e:
        # Handle database errors appropriately
        print(f"Error: {e}")
        return None
    finally:
        if connection.is_connected():
            connection.close()
            print("MySQl connection is closed")


def authenticate_user(user_email:str,plain_password:str):
    user = get_user_by_email(user_email)
    print(user)
    if not user:
        return False
    if not verify_password(plain_password,user.password):
        return False
    return user

def create_access_token(data:dict,expires_delta:timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_authenticate_user(token: Annotated[str, Depends(outh2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email: str = payload.get("sub")
        if user_email is None:
            raise credentials_exception
        token_data = TokenData(email=user_email)

    except ExpiredSignatureError:
        raise HTTPException(status_code=403,detail="Token expired! Please sign-in again")
    except JWTError:
        raise credentials_exception
    
    user = get_user_by_email(user_email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

    
@app.post("/Authorisation")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],) -> Token:
    email = form_data.username
    user = authenticate_user(email,form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect mail or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@app.get("/users_details/", response_model=UserDetails)
async def get_users_details(user_id: int, authenticated_user: UserModel = Depends(get_authenticate_user)):
    user = get_user_by_id(user_id)
    if user:
        return UserDetails(name=user.name, email=user.email, referral_code=user.referral_code, timestamp=user.timestamp)
    else:
        raise HTTPException(status_code=404, detail="User not found")


@app.get("/referral_details/", response_model=List[UserDetails])
async def get_specific_referral_details(referral_code: str, 
                                        authenticated_user: Annotated[UserModel, Depends(get_authenticate_user)],
                                        limit: Optional[int] = 10, 
                                        offset: Optional[int] = 0):
    
    users = get_users_by_referral_code(referral_code)
    if users:
        user_details_list = []
        for user in users[offset:offset+limit]:
            user_details_list.append(UserDetails(name=user.name, email=user.email, referral_code=user.referral_code, timestamp=user.timestamp))
        return user_details_list
    else:
        raise HTTPException(status_code=404, detail="At this moment, no users have utilized your referral code for referrals.")



@app.post("/register/")
async def register_user(user_data: UserModel):
    connection = None
    try:
        connection = db_connection_pool.get_connection()
        cursor = connection.cursor(dictionary=True)

        # Check if email already exists
        sql_insert_user_query = f"SELECT * FROM users_table WHERE email = %s"
        cursor.execute(sql_insert_user_query, (user_data.email,))
        cursor.fetchone()
        if cursor.fetchone():
            raise HTTPException(status_code=400,detail="This email is already registered!")
            
        # Hash the provided password before storing it
        hashed_password = get_password_hash(user_data.password)

        # Insert new user into the database
        sql_insert_user_query = "INSERT INTO users_table (name, email, password, referral_code) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql_insert_user_query, (user_data.name, user_data.email,hashed_password, user_data.referral_code))

        # new user ID
        new_user_id = cursor.lastrowid
        connection.commit()
        
        return {"message":f"Registration Successful! Your unique ID is: {new_user_id}"}
    
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    finally:
            if connection.is_connected():  # Check if connection is connected
                connection.close()
                print("MySQL connection is closed")

        


