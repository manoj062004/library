import mysql.connector
import sys

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






def is_fav(user_email, book_id):
    query = "SELECT * FROM favorites WHERE user_email = %s AND book_id = %s"
    cursor.execute(query, (user_email, book_id))
    return cursor.fetchone() is not None



def add_favorite(user_email,book_id,book_title, cover_url):
    try:
        query = "SELECT * FROM favorites WHERE user_email = %s AND book_id = %s"
        cursor.execute(query,(user_email,book_id))
        if cursor.fetchone():
            return "Book is already in favroites !"
        
        insert_query = "INSERT INTO favorites (user_email, book_id, book_title, cover_url) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, (user_email, book_id, book_title, cover_url))
        conn.commit()
        return "Added to Your favorites!"
    
    except mysql.connector.Error as e:
        return f"Error: {e}"



def remove_favorite(user_email,book_id):
     query = "DELETE FROM favorites WHERE user_email = %s AND book_id = %s"
     cursor.execute(query, (user_email, book_id))
     conn.commit()

def get_favorites(user_email):
    query = "SELECT book_id, book_title, cover_url FROM favorites WHERE user_email = %s"
    cursor.execute(query, (user_email,))
    return cursor.fetchall()



def add_review(book_id, user_email, rating, comment):
    
    try:

        query = "SELECT * FROM reviews WHERE user_email = %s AND book_id = %s"
        cursor.execute(query,(user_email,book_id))
        exiting = cursor.fetchone()

        if exiting:
            query_update = "UPDATE reviews SET rating = %s, review_text = %s WHERE book_id = %s AND user_email = %s"
            cursor.execute(query_update, (rating, comment, book_id, user_email))
            conn.commit()
            print("updated")
            return "updated Your Suggestion"
            
        else:
            insert_query = "INSERT INTO reviews (book_id, user_email, rating, review_text) VALUES (%s, %s, %s, %s)"
            cursor.execute(insert_query, (book_id, user_email, rating, comment))
            conn.commit()
            print("added")
            return "Add Your Suggestion"
            
    
    except mysql.connector.Error as e:
        return f"Error: {e}"
    



def get_reviews(book_id):
    try:
        query = "SELECT user_email, rating, review_text FROM reviews WHERE book_id = %s ORDER BY id DESC"
        cursor.execute(query, (book_id,))
        reviews = cursor.fetchall()
        return reviews
    except Exception as e:
        print(f"❌ Error fetching reviews: {e}")
        return []


def delete_review(review_id, user_email):
    pass


