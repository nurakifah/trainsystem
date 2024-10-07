from flask import Flask, render_template, request, redirect, url_for, g, session, flash
import pymysql
import pymysql.cursors 
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database configuration
db_host = "localhost"
db_user = "root"
db_password = ""
db_name = "train-ticket"

# Function to get the database connection
def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(host=db_host, user=db_user, password=db_password, database=db_name)
        g.cursor = g.db.cursor()
    return g.db, g.cursor

# Close the database connection when the application shuts down
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()



# Login Form
@app.route("/login", methods=['GET', 'POST'])
def login():
    error_message = None 
    if request.method == 'POST':
        user_email = request.form['email']
        user_password = request.form['password']

        # Get the database connection and cursor
        db, cursor = get_db()

        # Execute an SQL query to check if the email and password match
        query = "SELECT * FROM user WHERE user_email=%s AND user_password=%s"
        cursor.execute(query, (user_email, user_password))
        user_data = cursor.fetchone()

        if user_data:
            # Set the user session data
            session['user_id'] = user_data[0]
            session['name'] = user_data[1]
            session['email'] = user_data[2]
            session['password'] = user_data[3]
            session['phoneNum'] = user_data[4]
            error_message = "Login Successfully."

            return redirect(url_for('home'))  # Change 'index' to the actual name of your index route                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
        else:
             error_message = "Invalid email or password. Please try again."
    
    return render_template('login.html', error_message=error_message)


# Signup Form
@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Retrieve user information from the form
        user_name = request.form['name']
        user_email = request.form['email']
        user_password = request.form['password']
        user_phoneNum = request.form['phoneNum']

        # Store the user information in the database
        user_id = store_user_in_database(user_name, user_email, user_password, user_phoneNum )
        # Redirect to a success page or do additional processing

        # Redirect to the login page after successful form submission
        return redirect(url_for('login', user_id=user_id))

    # Display the signup form
    return render_template('signup.html')


# End of get the user input for signup session
def store_user_in_database(user_name, user_email, user_password, user_phoneNum):
    # Get the database connection and cursor
    db, cursor = get_db()

    # Execute an SQL query to insert user information into the database
    query = "INSERT INTO user (user_name, user_email, user_password, user_phoneNum) VALUES (%s, %s,%s, %s)"
    cursor.execute(query, (user_name, user_email, user_password, user_phoneNum ))

    # Commit the changes
    db.commit()

@app.route("/", methods=['GET', 'POST'])
def home():
    user_id = session.get('user_id')
    if request.method == 'POST':
        # Retrieve user information from the form
        source_station = request.form.get('origin')
        destination_station = request.form.get('destination')
        departure_time = request.form.get('departureDate')
        arrival_time = request.form.get('returnDate')
        trip_type = request.form.get('tripType')

        # Save the form data in the session
        session['source_station'] = source_station
        session['destination_station'] = destination_station
        session['departure_time'] = departure_time
        session['arrival_time'] = arrival_time
        session['trip_type'] = trip_type 

        # Redirect to the appropriate route based on trip type
        if trip_type == 'twoWay':
            return redirect(url_for('twoWay'))
        else:
            return redirect(url_for('trainList'))

    return render_template('index.html', user_id=user_id)

@app.route("/trainList", methods=['GET', 'POST'])
def trainList():
    user_id = session.get('user_id')
    train_id = session.get('train_id')
    
   
   # Get the database connection and cursor
    db, cursor = get_db()

    # Retrieve the search criteria from the session
    source_station = session.get('source_station')
    destination_station = session.get('destination_station')
    departure_time = session.get('departure_time')

    # Query the database for trains matching the user input
    query = """
    SELECT * FROM train
    WHERE source_station = %s
    AND destination_station = %s
    AND departure_date = %s
    """
    cursor.execute(query, (source_station, destination_station, departure_time))
    trains = cursor.fetchall()  # Fetch all matching trains

    # Check if there are no trains available
    if not trains:
        message = "There is no train available on that table."
        return render_template('train-list.html', trains=[], message=message)

    fare_data = {train[0]: train[9] for train in trains}  # Assuming train[0] is train_id and train[9] is fare
    session['fare_data'] = fare_data

    # Pass the queried train data to the template
    return render_template('train-list.html', trains=trains, source_station=source_station, destination_station=destination_station, user_id=user_id, train_id=train_id)

@app.route("/twoWay", methods=['GET', 'POST'])
def twoWay():
    user_id = session.get('user_id')
    db, cursor = get_db()
    
    source_station = session.get('source_station')
    destination_station = session.get('destination_station')
    departure_time = session.get('departure_time')
    arrival_time = session.get('arrival_time')
    
    # Query for departure trains
    departure_query = """
    SELECT * FROM train
    WHERE source_station = %s
    AND destination_station = %s
    AND departure_date = %s
    """
    cursor.execute(departure_query, (source_station, destination_station, departure_time))
    departure_trains = cursor.fetchall()
    
    # Query for return trains
    return_query = """
    SELECT * FROM train
    WHERE source_station = %s
    AND destination_station = %s
    AND departure_date = %s
    """
    cursor.execute(return_query, (destination_station, source_station, arrival_time))
    return_trains = cursor.fetchall()

    # Render the template with the retrieved data
    return render_template('twoWay-train-list.html', departure_trains=departure_trains, return_trains=return_trains, source_station=source_station, destination_station=destination_station, user_id=user_id)

@app.route("/selectTrain", methods=['GET', 'POST'])
def selectTrain():
    return render_template('train-seat.html')


@app.route("/trainSeat", methods=['GET', 'POST'])
def trainSeat():
    user_id = session.get('user_id')
    train_id = session.get('train_id')
    fare_data = session.get('fare_data', {})  # Default to an empty dict if 'fare_data' is not in session

    # Get the fare for the specific train_id
    fare = fare_data.get(train_id, 0)  # Default to 0 if train_id is not found in fare_data
    
    if request.method == 'POST':
        book_coach = request.form['book_coach']
        book_seat = request.form['book_seat']
        
        # Insert into booking table
        db, cursor = get_db()  # Ensure you have a function to get the DB connection
        query = """
        INSERT INTO booking (user_id, train_id, book_coach, book_seat, fare) VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (user_id, train_id, book_coach, book_seat, fare))
        db.commit()  # Commit the transaction
        
        flash("Booking successful!", "success")
        return redirect(url_for('invoice'))  # Redirect to a confirmation page or similar
    
    return render_template('train-seat.html', user_id=user_id, train_id=train_id, fare=fare)

@app.route("/invoice")
def invoice():
    return render_template('invoice.html')


if __name__ == '__main__':
    app.run(debug=True)