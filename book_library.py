import mysql.connector
import streamlit as st
import time
import sys
import base64
import random
import requests
from PIL import Image
import random, smtplib, ssl, hashlib
from email.mime.text import MIMEText
from favorites import * #add_favorite, remove_favorite, get_favorites ,is_fav


# Establish connection

try:
   
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        database="library_database"
    )
    cursor = conn.cursor()
    print("Connected to MySQL!", flush=True)

except mysql.connector.Error as err:
    print("=== MySQL Error Details ===")
    print(f"Error Code: {err.errno}")
    print(f"SQL State: {err.sqlstate}")
    print(f"Error Message: {err.msg}")
    print("==========================")

    if err.errno == 2003:
        print("Error: Could not connect to MySQL server. Please check if the server is running on localhost:3306.")
    elif err.errno == 1049:  # Error code for "Unknown database"
        print("Error: The specified database 'library_database' does not exist.")
    elif err.errno == 1045:  # Error code for "Access denied"
        print("Error: Access denied. Please check your username and password.")
    else:
        # Any other MySQL errors
        print(f"Database error occurred: {err}")

    # Script ko yahin terminate karen
    sys.exit(0)  # Non-zero exit code indicates an error

except Exception as e:

    print("=== Unexpected Error Details ===")
    print(f"Error Type: {type(e).__name__}")
    print(f"Error Message: {str(e)}")
    print("===============================")
    sys.exit(1)





# Initialize session state for book selection
if "selected_book" not in st.session_state:
    st.session_state.selected_book = None


# Function to fetch book details with api 
def get_book_details(queries):
    books = []
    
    if isinstance(queries, str):  # Single query case
        queries = [queries]

    for query in queries:
        url = f"https://openlibrary.org/search.json?title={query}"
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                books.extend(data.get("docs", []))  # Add results to books list
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Error fetching books: {e}")

    return books




def display_book_banners(books):
    if not books:
        return

    st.subheader("📚 Search Results:")

    # ✅ Filter only books that have a cover image
    books_with_covers = [book for book in books if book.get("cover_i")]

    if not books_with_covers:
        st.write("❌ No books with covers found. Try another search.")
        return

    for i in range(0, len(books_with_covers), 3):  # Show 3 books per row
        cols = st.columns(3)  # Create 3 columns
        for j in range(3):
            if i + j < len(books_with_covers):
                book = books_with_covers[i + j]
                title = book.get("title", "Unknown Title")
                cover_id = book.get("cover_i") 
                
                # ✅ Use only books that have a valid cover ID
                img_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"

                with cols[j]:
                    if st.button("book detail", key=f"book_{i+j}"):
                        st.session_state["selected_book"] = book  # Store selected book
                        st.rerun()
                    st.image(img_url, caption=title[:20], use_container_width=True)



                    



# Function to show book details
def display_book_details(book):
    st.subheader("📖 Book Details")
    st.write(f"**Title:** {book.get('title', 'Unknown Title')}")
    st.write(f"**Author(s):** {', '.join(book.get('author_name', ['Unknown']))}")
    st.write(f"**First Published Year:** {book.get('first_publish_year', 'N/A')}")
    
    cover_id = book.get("cover_i")
    book_id = book.get("key", "N/A")
    book_title = book.get("title",'Unknown Title')

    if cover_id:
        img_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
        st.image(img_url, use_container_width=200)



    if is_fav(st.session_state['user_email'],book_id):
        if st.button("❌ Remove favorite"):
            remove_favorite(st.session_state['user_email'],book_id)
            st.success(f"{book_title} remove your favroite")
            time.sleep(2)
            st.rerun()
    else:
        if st.button("❤️ Add to Favorites",key=f"fav_{book_id}"):
            add_favorite(st.session_state["user_email"], book_id, book_title, cover_id)
            st.success(f"{book_title} add your favroite")
            time.sleep(2)
            st.rerun()

    st.subheader("User Reviews")
    reviews = get_reviews(book_id)

    if reviews:
        for review in reviews:
            user_email, rating, comment = review
            split = user_email[:user_email.index('@')]
            st.write(f"**{split}** ⭐ {rating}/5")
            st.write(f"💬 {comment}")
            st.markdown("---")
    else:
        st.info("No reviews yet. Be the first to review!")

    st.write("Rate This Book")
    rating = st.slider("Give Your Rating",1,5)
    review =  st.text_area("write review")

    if st.button("Submit"):
        if not all([book_id,st.session_state['user_email'],rating,review]):
            st.error("⚠️ All fields are required!")
            
        else:
            add_review(book_id,st.session_state['user_email'],rating,review)
            st.success("add your suggestion")



    
    if st.button("🔙 Back to Search",key= st.session_state['selected_book']):
        del st.session_state["selected_book"]
        st.rerun()








# book banners

def banner(bann):
    books_with_cover = [book for book in bann if book.get("cover_i")]

    if not books_with_cover:
        st.write("❌ No books with covers found. Try another search.")
        return

    st.title(f"Showing {len(books_with_cover)} Books")

    for i in range(0, len(books_with_cover), 7):  # Show 5 books per row
        cols = st.columns([1, 0.1, 1, 0.1, 1, 0.1, 1, 0.1, 1])
        book_index = 0

        for ban in range(0, 9, 2):  # Access columns with spacing
            if i + book_index < len(books_with_cover):
                book = books_with_cover[i + book_index]
                title = book.get("title", "Unknown Title")
                cover_id = book.get("cover_i")

                img_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"

                with cols[ban]:
                    st.image(img_url, use_container_width=True)
                    st.caption(title[:20])

                book_index += 1



# full refesh page javascript 
def full_refresh():
    st.experimental_set_query_params(refresh="2") 
    st.rerun()


if "page" not in st.session_state:
    st.session_state['page'] = 'login'


if "register_clicked" not in st.session_state:
    st.session_state.register_clicked = False



# ✅ Function to Set Background from Local Image
def set_bg_from_local(image_file):
    with open(image_file, "rb") as img_file:
        encoded_img = base64.b64encode(img_file.read()).decode()

    page_bg = f"""
    <style>
    .stApp {{
        background: url("data:image/png;base64,{encoded_img}");
        background-size: cover;
    }}

    .blur-box {{
     position: absolute;
    top :220px;
     left: 50%;
     transform: translate(-50%, -50%);
     width: 110%;
     padding: 20px;
     background: rgba(255, 255, 255, 0.2);
     border-radius: 15px;
     backdrop-filter: blur(12px);
     -webkit-backdrop-filter: blur(12px);
     box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
     text-align: center;
     height: {"800px" if st.session_state.register_clicked else "500px"};
     font-size: 25px;
     color:#000;

    }}

    </style>
    """
    st.markdown(page_bg, unsafe_allow_html=True)

# ✅ Local Image Ka Path 
set_bg_from_local("background3.jpg")



 #  register function
def register(emaill,password,name,last_name,path):

    if not all([emaill, password, name, last_name, path]):
        st.error("⚠️ All fields are required!")
        return
    
    if is_email_registered(emaill):
        st.error("⚠️ Email already registered! Please login.")
        return
    try:
        photo_data = path.read()  # photo read binary
        cursor.execute("INSERT INTO auth_data (email, password_hash, Name, Last_name, photo) VALUES (%s, %s, %s, %s, %s)", 
                    (emaill, password, name, last_name, photo_data))
        conn.commit()
        st.success("✅ Registration Successful! Redirecting to Login...")
        time.sleep(2)
        st.session_state["page"] = "login"
        st.rerun()
    except mysql.connector.Error as e:
        st.error(f"Error {e}")



# login form
def login(l_login,l_pass):
    quer = 'SELECT * FROM auth_data WHERE email = %s AND password_hash = %s'

    cursor.execute(quer,(l_login,l_pass))
    result = cursor.fetchone()

    if result:
        st.success('Login Sucessfully')
        print(l_login)
        time.sleep(3)
        st.session_state["page"] = "home"
        st.session_state["user_email"] = l_login  

        def userimage(email):
            cursor.execute("SELECT name,Last_name ,photo FROM auth_data WHERE email = (%s)", (email,))
            res_img = cursor.fetchone()
            
            if res_img:
                name,last_name,us_img = res_img
                return name,last_name,us_img
            return None,None,None
        
        name, last_name, user_img = userimage(l_login)

        st.session_state["page"] = "home"
        st.session_state["user_email"] = l_login
        st.session_state["user_name"] = name
        st.session_state["user_last_name"] = last_name
        st.session_state["user_img"] = user_img
        st.rerun()
    else:
        st.error("Something Went Wrong Cheak id password")





def is_email_registered(email):
    cursor.execute("SELECT * FROM auth_data WHERE email = %s", (email,))
    return cursor.fetchone() is not None


# email sent funtion 

SMTP_SERVER, SMTP_PORT = "smtp.gmail.com", 465
SENDER_EMAIL, PASSWORD = "billuyadav431@gmail.com", "dfwrdvepilegnghw"

def send_otp(email, otp):
    html_content = f"""
    <html>
    <body style="background-color: #121212; color: white; font-family: Arial, sans-serif; text-align: center; padding: 20px;">
        <div style="max-width: 400px; margin: auto; background: #1e1e1e; padding: 83px; border-radius: 10px; box-shadow: 0px 0px 10px rgba(255, 255, 255, 0.1);">
            <img src="https://books2ebooks.eu/sites/default/files/inline-images/content-front-page-open-book.png" alt="Book Icon" style="width: 80px; margin-bottom: 20px;">
            <h2 style="color: #ddd;">Your One-Time Verification Code</h2>
            <div style="background: #333; padding: 15px; border-radius: 10px; display: inline-block;">
                <h1 style="margin: 0; font-size: 32px; letter-spacing: 5px; color: #00ffcc;">{otp}</h1>
            </div>
            <p>This code is valid for the next <b>10 minutes</b>.</p>
            <p>If you did not request this, please ignore this email.</p>
            <br>
            <p style="font-size: 12px; color: gray;">Best regards,<br>Library OTP Team</p>
        </div>
    </body>
    </html>
    """


    msg = MIMEText(html_content, "html")
    msg["From"] = "Library OTP <your_email@gmail.com>"
    msg["To"] = email
    msg["Subject"] = "Registration to BookNest "

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=ssl.create_default_context()) as server:
            server.login(SENDER_EMAIL, PASSWORD)
            server.sendmail(SENDER_EMAIL, email, msg.as_string())
        st.success("✅ OTP Sent!")
    except:
        st.error("❌ Failed to send OTP.")


if "otp_sent" not in st.session_state:
    st.session_state.otp_sent = False
if "otp" not in st.session_state:
    st.session_state.otp = None





if st.session_state['page'] == 'login':
    st.markdown('<marquee behavior="alternate"><h2>Welcome to BookNest</h2></marquee>',unsafe_allow_html=True)
    st.write('Login Your account')
    email = st.text_input("Email").lower()
    password = st.text_input("Password", type="password")

    hased_password = hashlib.sha256(password.encode()).hexdigest()
    if st.button("Login"):
        login(email, hased_password)

    if st.button("Register Instead"):
        st.session_state.register_clicked = not st.session_state.register_clicked
        st.session_state["page"] = "register"
        st.rerun()


# registerion session 




elif st.session_state["page"] == "register":
    st.title("Register Here")
    
    name, last_name = st.text_input("First Name"), st.text_input("Last Name")
    email = st.text_input("Email").lower()
    password = st.text_input("Password", type="password")
    path = st.file_uploader("Upload Photo", type=['jpg','png'])

    
    if st.button("Submit") and not st.session_state.otp_sent:
        if is_email_registered(email):
            st.success("✅ Email already registered! Logging in...")
        else:
            st.session_state.otp = str(random.randint(100000, 999999))
            send_otp(email, st.session_state.otp)
            st.session_state.otp_sent = True

    if "otp" in st.session_state:
        user_otp = st.text_input("Enter OTP")
        if st.button("Verify & Register"):
            if user_otp == st.session_state.otp:
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                register(email, hashed_password, name, last_name, path)  # Save to DB
            else:
                st.error("❌ Incorrect OTP!")
        

elif st.session_state["page"] == "home":
    st.title("Welcome to BookNest 🎉")
    
    user_email = st.session_state.get("user_email", None)
    user_name = st.session_state.get("user_name", "")
    user_last_name = st.session_state.get("user_last_name", "")
    user_img = st.session_state.get("user_img", None)
  
    if user_img:
        st.sidebar.image(user_img, width=50)
        st.sidebar.write(f"{user_name} {user_last_name}")

        st.sidebar.subheader("⭐ My Favorite Books")

    favorites = get_favorites(st.session_state["user_email"])
    favorite_option = st.sidebar.selectbox("Select an option", ["list fav", ""])

    if favorite_option == 'list fav':
        for book_id, title, cover_url in favorites:
            with st.sidebar:
                url = f"https://covers.openlibrary.org/b/id/{cover_url}-L.jpg"
                st.image(url, width=50)
                st.write(title[:20])
                if st.button("❌ Remove", key=f"remove_{book_id}"):
                    remove_favorite(st.session_state["user_email"], book_id)
                    st.rerun()


    query = st.text_input("Enter book name: ")
    fin_book = get_book_details(query)[:10]
    baaner_book = get_book_details('Rich dad')[:10]

    if st.session_state.selected_book:
        display_book_details(st.session_state["selected_book"])
    else:
        display_book_banners(fin_book)
        banner(baaner_book)

    if st.button("Logout"):
        st.session_state["page"] = "login"
        st.rerun()  

