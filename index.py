import time,requests
from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_mail import Mail, Message
from datetime import timedelta
from datetime import timedelta

# Flask App Initialize
app = Flask(__name__)
app.secret_key = "anykey"
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['SESSION_REFRESH_EACH_REQUEST'] = True

app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Your SMTP server
app.config['MAIL_PORT'] = 465  # Port for your SMTP server
app.config['MAIL_USE_TLS'] = False  # Use TLS (True or False)
app.config['MAIL_USE_SSL'] = True  # Use SSL (True or False)
app.config['MAIL_USERNAME'] = 'mail@mail.com'  # Your email username
app.config['MAIL_PASSWORD'] = '12345'  # Your email password
app.config['MAIL_DEFAULT_SENDER'] = 'mail@mail.com'  # Default sender email address

app.permanent_session_lifetime = timedelta(hours=8)
mail = Mail(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/sess", methods=["GET", "POST"])
def sess():
    print(session.get('is_login'), session.get("email"), session.get("faculty_id"), session.get("name"), session.get("phone"), session.get("clg_id"))
    return "Check Print Statment"


@app.route("/admin_only", methods=["GET", "POST"])
def only_admin():
    if session.get("admin_login") == True:
        url = "https://hetpatel.in/API/fetch_admin_data.php"
        response = requests.get(url=url)
        result = response.json()
        total_clg=result["total_colleges"]
        total_student=result["total_students"]
        all_event=result["event_data"]
        return render_template("admin_showalldata.html", college=total_clg, student=total_student, events=all_event)        
    else:
        flash("Please Login First", "danger")
        return redirect("/login")

@app.route("/admin_student_show", methods=["GET", "POST"])
def admin_student_show():
    if session.get("admin_login") == True:
        url = "https://hetpatel.in/API/admin_student_show.php"
        response = requests.get(url=url)
        result = response.json()
        data=result["data"]

        return render_template("admin_all_student_list.html",  data=data)        
    else:
        flash("Please Login First", "danger")
        return redirect("/login")

@app.route("/admin_faculty_show", methods=["GET", "POST"])
def admin_faculty_show():
    if session.get("admin_login") == True:
        url = "https://hetpatel.in/API/admin_faculty_fetch.php"
        response = requests.get(url=url)
        result = response.json()
        data=result["data"]

        return render_template("admin_all_faculty_list.html",  data=data)        
    else:
        flash("Please Login First", "danger")
        return redirect("/login")

@app.route("/admin_events/<int:id>", methods=["GET", "POST"])
def only_admin_events(id):
    if session.get("admin_login") == True:
        url = f"https://hetpatel.in/API/test_admin.php?event_id={id}"
        response = requests.get(url=url)
        result = response.json()
        data=[]

        if result["error"] == True:
            return render_template("admin_event_show.html", data=data)
        else:
            return render_template("admin_event_show.html", data=result["data"])
    else:
        flash("Please Login First", "danger")
        return redirect("/login")


@app.route("/faculty_events/<int:id>", methods=["GET", "POST"])
def faculty_events(id):
    if session.get("is_login") == True:
        clg_id = session.get("clg_id")
        url = f"https://hetpatel.in/API/test_faculty.php?event_id={id}&clg_id={clg_id}"
        response = requests.get(url=url)
        result = response.json()
        data=[]

        if result["error"] == True:
            return render_template("faculty_event_show.html", data=data)
        else:
            return render_template("faculty_event_show.html", data=result["data"])
    else:
        flash("Please Login First", "danger")
        return redirect("/login")


@app.route("/", methods=["GET", "POST"])
def welcome():
    # if session.get("is_login") == True:
    #     return redirect("/home")
    # else:
    url = "https://hetpatel.in/API/fetch_all_events.php"
    response= requests.get(url=url)
    result = response.json()
    music_data = result["data"]["Music"]
    dance_data = result["data"]["Dance"]
    litertaure_data = result["data"]["Literature"]
    theatre_data = result["data"]["Theatre"]
    fine_arts_data = result["data"]["Fine Arts"]
    return render_template("welcome.html", music_data=music_data,dance_data=dance_data,litertaure_data=litertaure_data,theatre_data=theatre_data,fine_arts_data=fine_arts_data  )

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # This try and except block check if any person is already logged in
    if session.get("is_login") == True:
        return redirect("/home")
    else:
        # User reached route via POST (as by submitting a form via POST)
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")
            print(email, password)
            # Ensure required fields are submitted
            if email == "" and password == "":
                return render_template("faculty_signin.html", message="Please Provide All Required Details")

            # Ensure Email was submitted
            if not email:
                return render_template("faculty_signin.html", message="Please Provide Email")

            # Ensure password was submitted
            if not password:
                return render_template("faculty_signin.html", message="Please enter a password")

            # Query database for username
            try:
                url = "https://hetpatel.in/API/loginapi.php"
                params = {
                    "email_id": email.lower().strip(),
                    "password": password.strip()
                }
                r1 = requests.post(url=url, data=params)
                result = r1.json()
                if (result["error"] == True) or (not check_password_hash(result["user"]["password"], password)) :
                    return render_template("faculty_signin.html", message="Incorrect email or password!")

                elif email == "techfest@sal.edu.in":
                    session["admin_login"]=True
                    return redirect("/admin_only")
                else:           
                    session['is_login'] = True
                    session["email"] = result["user"]["email"]
                    session["faculty_id"] = result["user"]["id"]
                    session["name"] = result["user"]["fullname"]
                    session["phone"] = result["user"]["phone_number"]
                    session["clg_id"] = result["user"]["clg_id"]
                    return redirect("/home")
                                
            except Exception as e:
                print("Exception in login",e)
                return render_template("faculty_signin.html", message="Error while connecting with database")
        # User reached route via GET (as by clicking a link or via redirect)
        else:
            return render_template("faculty_signin.html")


# @app.route("/faculty_signup", methods=["POST", "GET"])
# def faculty_signup():
#     ''' Signup Page '''
#     # Check if user is already logged in
#     if session.get("is_login") == True:
#         return redirect("/home")
#     else:
#         try:
#             url="https://hetpatel.in/API/fetch_college.php"
#             response=requests.get(url=url)
#             result=response.json()
#             data=result["data"]
#         except Exception as e:
#             return render_template("faculty_signup.html", message="Sorry! Something Unexpected Happened")        
#         if request.method == "POST":
#             name = request.form.get("name")
#             email = request.form.get("email")
#             clg_id = request.form.get("clg_id")
#             designation = request.form.get("designation")
#             phone_no = request.form.get("phone")
#             print(name, email, clg_id, designation, phone_no)

#             # User input validation
#             if name == "" and email == "" and clg_id == "" and designation == "" and phone_no == "":
#                 return render_template("faculty_signup.html", message="Please Enter All Required Details", data=data)

#             elif not name:
#                 return render_template("faculty_signup.html", message="Please Enter Name", data=data)

#             elif not clg_id:
#                 return render_template("faculty_signup.html", message="Please Select Valid College", data=data)

#             elif not email:
#                 return render_template("faculty_signup.html", message="Please Enter An Email", data=data)

#             elif not phone_no:
#                 return render_template("faculty_signup.html", message="Please Enter Your Phone No", data=data)

#             elif len(phone_no) > 10 or len(phone_no) < 10 or not phone_no.isdigit():
#                 return render_template("faculty_signup.html", message="Please Enter Your Phone No in 10 digit only", data=data)

#             elif not designation:
#                 return render_template("faculty_signup.html", message="Please Enter Designation", data=data)

#             password = generate_password()
#             hash = generate_password_hash(password)
#             print(password)
#             try:
#                 clg_ids = []
#                 faculty_already_mail=[]
#                 url1 = "https://hetpatel.in/API/fetch_faculty_login.php"
#                 response1 = requests.get(url=url1)
#                 result1 = response1.json()
#                 if result1["error"] == False:
#                     for row in result1["data"]:
#                         faculty_already_mail.append(row["email"])
#                         clg_ids.append(row["clg_id"])
#                     if email in faculty_already_mail:
#                         return render_template("faculty_signup.html", message=f'The email "{email}" is already registered kindly use another email', data=data)

#                     if clg_ids.count(int(clg_id)) >= 2:
#                         return render_template("faculty_signup.html", message=f"Sorry! Your college has reached it's registation limit", data=data)                
#             except Exception as e:
#                 print("Exception 1 in Signup", e)
#                 return render_template("faculty_signup.html", message="Error while connecting with database")
#             try:            
#                 mess = """ Welcome to the Core Committee of Xitij """
#                 message = Message(mess, recipients=[email])
#                 message.html = render_template(
#                     "greeting.html", email=email, password=password, name=name)
#                 message.body = message.html
#                 mail.send(message)
#                 pass
#             except Exception as e:
#                     print("Exception 2 in Signup", e)
#                     return render_template("faculty_signup.html", message="Something went wrong! Mail Couldn't be Sent")
#             try:
#                 url2 = "https://hetpatel.in/API/signupapi.php"
#                 params = {
#                     "fullname": name.title().strip(),
#                     "email":email.lower().strip(),
#                     "password":hash,
#                     "clg_id":clg_id,
#                     "designation":designation.strip().title(),
#                     "phone_number":phone_no
#                 }
#                 response2 = requests.post(url=url2, data=params)
#                 result2 = response2.json()
#                 print("Signup Sucess", result2["message"])
#                 flash("Signup Succes! Credentials has been sent to your Registered Email", "success")
#                 return redirect("/login")                
          
#             except Exception as e:
#                 print("Exception 3 in Signup", e)
#                 return render_template("faculty_signup.html", message="Error while connecting with database")

#         else:
#             return render_template("faculty_signup.html", data=data)


@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id if found
    try:
        session.clear()
    except:
        pass
    # Redirect user to login form
    return redirect("/")




# @app.route("/addstudent", methods=["POST", "GET"])
# def add_student():
#     ''' Signup Page '''
#     # Check if user is already logged in
#     if not session.get("is_login"):
#         flash("Please Login First","danger")
#         return redirect("/login")
#     else:
#         if request.method == "POST":
#             student_name = request.form.get("name")
#             clg_id = session.get("clg_id")
#             enroll_no = request.form.get("enroll_no")
#             current_sem = request.form.get("current_sem")
#             phone_no = request.form.get("phone")
#             print(student_name, clg_id, enroll_no, current_sem, phone_no)          

#             # User input validation
#             if student_name == "" and enroll_no == "" and current_sem == "" and clg_id == "" and phone_no == "":
#                 return render_template("student_signup.html", message="Please Enter All Required Details")

#             elif not student_name:
#                 return render_template("student_signup.html", message="Please Enter Student Name")

#             elif not phone_no:
#                 return render_template("student_signup.html", message="Please Enter Phone Number")
            
#             elif len(phone_no) > 10 or len(phone_no) < 10 or not phone_no.isdigit():
#                 return render_template("student_signup.html", message="Please Enter Phone No in 10 Digit Only")
            
#             elif not enroll_no or not enroll_no.isdigit():
#                 return render_template("student_signup.html", message="Please Enter Correct Enrollment Number")
            
#             elif not current_sem or not current_sem.isdigit() or int(current_sem)>12:
#                 return render_template("student_signup.html", message="Please Enter Correct Semester")
            
#             enroll_no = enroll_no.strip()
#             phone_no = phone_no.strip()

#             try:
#                 url1 = "https://hetpatel.in/API/add_student.php"
#                 params = {
#                     "name": student_name.title().strip(),
#                     "clg_id": clg_id,
#                     "enroll_no":int(enroll_no),
#                     "current_sem":int(current_sem),
#                     "phone_no":int(phone_no),
#                 }
#                 r2 = requests.post(url=url1, data=params)
#                 result = r2.json()
#                 er=result["error"]
#                 er_type=result["error_type"]
#                 if er == True and er_type == "phone":
#                         return render_template("student_signup.html", message=result["message"])
#                 elif er == True and er_type == "enroll":
#                         return render_template("student_signup.html", message=result["message"])
#                 else:
#                     return render_template("student_signup.html", message="Student Added Successfully")                             
#             except Exception as e:
#                 return render_template("student_signup.html", message="Error while connecting with database")

#         else:
#             return render_template("student_signup.html")


@app.route("/home", methods=['POST', 'GET'])
def homepage():
    if not session.get("is_login"):
        flash("Please Login First","danger") 
        return redirect("/login")
    else:
        student_register=0
        total_events=0
        solo_register=0
        team_register=0        
        try:
            clg_id= session.get("clg_id")

            url = f"https://hetpatel.in/API/fetch_student.php?clg_id={clg_id}"
            reponse = requests.get(url=url)
            result = reponse.json()
            url1 = f"https://hetpatel.in/API/fetch_register_event.php?clg_id={clg_id}"
            response1 = requests.get(url=url1)
            result1 = response1.json()
            url2 = f"https://hetpatel.in/API/fetch_faculty_data.php?clg_id={clg_id}"
            response2 = requests.get(url=url2)
            result2 = response2.json()

            if result["query_error"] == True:
                return render_template("dashboard.html", student_register=student_register, solo_register=solo_register, team_register=team_register, total_events=total_events)

            elif result1["error"] == True:
                return render_template("dashboard.html", student_register=student_register, total_events=total_events, solo_register=solo_register, team_register=team_register)

            elif result2["error"] == True:
                return render_template("dashboard.html", student_register=student_register, total_events=total_events, solo_register=solo_register, team_register=team_register)
            
            elif result["query_error"] == False and result1["error"] == False and result2["error"] == False:
                team_data=result1["data"]["TEAM"]
                solo_data=result1["data"]["SOLO"]
                solo_register = len(result1["data"]["SOLO"])
                team_register = len(result1["data"]["TEAM"])
                student_register=len(result["query_data"])
                total_events=solo_register+team_register
                all_events_data = result2["data"]
                return render_template("dashboard.html",team_data=team_data, solo_data=solo_data,student_register=student_register, total_events=total_events, solo_register=solo_register, team_register=team_register, all_events_data=all_events_data)
        except Exception as e:
            print("Exception in data fetch", e)
        return render_template("dashboard.html", student_register=student_register, total_events=total_events, solo_register=solo_register, team_register=team_register)
    

@app.route("/student_list", methods=['POST', 'GET'])
def student_list():
    if not session.get("is_login"):
        flash("Please Login First","danger") 
        return redirect("/login")
    else:
        # student_register=0
        # total_events=0
        # solo_register=0
        # team_register=0        
        try:
            clg_id= session.get("clg_id")

            url = f"https://hetpatel.in/API/fetch_student.php?clg_id={clg_id}"
            reponse = requests.get(url=url)
            result = reponse.json()

            if result["query_error"] == True:
                return render_template("added_student_list.html",)

            elif result["query_error"] == False:
                data = result["query_data"]

            return render_template("added_student_list.html", data=data)
        except:
            pass
        return render_template("added_student_list.html",)
    
# @app.route("/solo_event", methods=["POST", "GET"])
# def solo_event():
#     ''' Signup Page '''
#     if not session.get("is_login"):
#         flash("Please Login First","danger")
#         return redirect("/login")
#     else:
#         if request.method == "POST":
#             event_id = request.form.get("event_id")
#             clg_id = session.get("clg_id")
#             enroll_no = request.form.get("enroll_no")
#             print(f"Event name: {event_id}, College Name: {clg_id}, Enroll No: {enroll_no}")

#             # User input validation
#             if event_id == ""  and enroll_no == "":
#                 flash("Please Enter All Required Details","warning")
#                 return redirect("/solo_event")

#             elif not event_id:
#                 flash("Please Select The Event","warning")
#                 return redirect("/team_event")

#             elif not enroll_no or not enroll_no.isdigit():
#                 flash("Please Provide The Enrollment as per GTU","warning")
#                 return redirect("/team_event")
            
#             enroll_no=enroll_no.strip()
            
#             try:
#                 clg_id = session.get("clg_id")
#                 faculty_id = session.get("faculty_id")

#                 url3 = f"https://hetpatel.in/API/fetch_solo_event_student.php?clg_id={clg_id}&enroll_no={enroll_no}"
#                 response3 = requests.get(url=url3)
#                 result3 = response3.json()

#                 url3 = "https://hetpatel.in/API/add_register_event.php"
#                 params = {
#                         "faculty_id":int(faculty_id),
#                         "event_id":int(event_id),
#                         "student_id":int(result3["data"][0]["id"]),
#                     }
#                 r2 = requests.post(url=url3, data=params)
#                 res = r2.json()
#                 flash("Student Registration For Solo Event SuccessFull", "success")
#                 return redirect("/home")
#             except Exception as e:
#                 print("Error in solo event 1",e)
#                 return render_template("solo_register.html", message="Error while connecting with database")
            
#         else:
#             try:
#                 clg_id = session.get("clg_id")

#                 url = f"https://hetpatel.in/API/fetch_student.php?clg_id={clg_id}"
#                 response = requests.get(url=url)
#                 result = response.json()

#                 url4 = f"https://hetpatel.in/API/fetch_solo_team.php?clg_id={clg_id}"
#                 response4 = requests.get(url=url4)
#                 result4 = response4.json()
#                 all_events = [
#                     {"Music": [{'Classical Vocal Solo': 39},{'Classical Instrumental Solo-Percussion': 43},
#                                {'Classical Instrumental Solo-Non-Percussion': 44},{"Light Vocal":38},{"Western Vocal":40},{"Western Instumental Solo":45}]},
#                     {"Dance": [{'Classical Dance': 47}]},
#                     {"Literary": [{'Elocution': 49}]},
#                     {"Theatre": [{'Mimicry': 55}]},
#                     {"Fine Arts": [{'On the Spot Painting': 57},
#                                 {'Collage': 61}, {'Poster Making': 58}, {'Clay Modeling': 60},
#                                 {'Cartooning': 59}, {'Rangoli': 56}, {'Spot Photography': 64}, {'Mehndi': 62}]}
#                 ]

#                 if result ["query_error"] == True:
#                     return render_template("solo_register.html")                
#                 elif result4["error"] == True:
#                     return render_template("solo_register.html", data=all_events, enroll_data=result["query_data"])
#                 elif result4["error"] == False:
#                     api_ids = set(item["id"] for item in result4["data"])
#                     # Iterate through the event categories
#                     for category in all_events:
#                         for category_name, events in category.items():
#                             updated_events = []
#                             # Iterate through the events in the category
#                             for event in events:
#                                 event_name, event_id = list(event.keys())[0], list(event.values())[0]
#                                 # Check if the event's ID is not in the set of API IDs
#                                 if event_id not in api_ids:
#                                     updated_events.append({event_name: event_id})
#                             # Update the category with events that aren't in the API response
#                             category[category_name] = updated_events

#                     # Remove categories with no events
#                     all_events = [category for category in all_events if list(category.values())[0]]
#                     return render_template("solo_register.html", data=all_events, enroll_data=result["query_data"])
#                 else:
#                     return render_template("solo_register.html")
#             except Exception as e:
#                 print("Error in solo event 2",e)
#                 return render_template("solo_register.html", message="Error while connecting with database")
    
# @app.route("/team_event", methods=["POST", "GET"])
# def team_event():
#     ''' Signup Page '''
#     if not session.get("is_login"):
#         flash("Please Login First","danger")
#         return redirect("/login")
#     else:
#         if request.method == "POST":
#             event_id = request.form.get("event_id")
#             clg_id = session.get("clg_id")
#             enroll_no = request.form.getlist("enroll_no")
#             enroll_no_list = [int(number) for number in enroll_no]
#             enroll_no_str = ', '.join(["'{}'".format(enrollment) for enrollment in enroll_no])
#             print(f"Event name: {event_id}, College Name: {clg_id}, Enroll No: {enroll_no}, Enroll list: {enroll_no_list}")

#             # User input validation
#             if event_id == ""  and enroll_no == []:
#                 flash("Please Enter All Required Details","warning")
#                 return redirect("/team_event")

#             elif not event_id:
#                 flash("Please Select The Event","warning")
#                 return redirect("/team_event")

#             elif not enroll_no or enroll_no==[]:
#                 flash("Please Select Proper Enrollment","warning")
#                 return redirect("/team_event")
            
#             event_id=event_id.strip()
                        
#             try:
#                 clg_id = session.get("clg_id")
#                 faculty_id = session.get("faculty_id")

#                 url1 = f"https://hetpatel.in/API/fetch_team_event_student.php?clg_id={clg_id}&enroll_no={enroll_no_str}"
#                 response1 = requests.get(url=url1)
#                 result1 = response1.json()

#                 url2 = f'https://hetpatel.in/API/fetch_event_table.php?event_id={event_id}'
#                 response2 = requests.get(url=url2)
#                 result2 = response2.json()  
#                 max_size=result2["data"][0]["max_size"]

#                 if len(enroll_no_list) > int(max_size):
#                     flash(f"The max size of this event is {max_size}, kindly select lower or exact no of student for this event","warning")
#                     return redirect("/team_event")
#                 for i in range(len(result1["data"])):
#                     url3 = "https://hetpatel.in/API/add_register_event.php"
#                     params = {
#                             "faculty_id": faculty_id,
#                             "event_id": event_id,
#                             "student_id":result1["data"][i]["id"]
#                         }
#                     r2 = requests.post(url=url3, data=params)
#                     res = r2.json()
#                     time.sleep(2)
#                 flash("Team Event Added Success", "success")
#                 return redirect("/home")
#             except Exception as e:
#                 print("Error in solo event 1",e)
#                 return render_template("team_register.html", message="Error while connecting with database")
#         else:
#             try:
#                 clg_id = session.get("clg_id")
#                 url2 = f"https://hetpatel.in/API/fetch_solo_team.php?clg_id={clg_id}"
#                 response2 = requests.get(url=url2)
#                 result2 = response2.json()

#                 url5 = f'https://hetpatel.in/API/fetch_student.php?clg_id={clg_id}'
#                 response5 = requests.get(url=url5)
#                 result5 = response5.json()

#                 all_events = [
#                     {"Music": [{'Group Song-Indian':41}, {'Group Song-Western':42}, {'Folk Orchestra':46}]},
#                     {"Dance": [{'Folk-Tribal Dance':48}]},
#                     {"Literary": [{'Quiz':51},{'Debate':50}]},
#                     {"Theatre": [{'One Act Play':52},{'Skits':53},{'Mime':54}]},
#                     {"Fine Arts": [{'Installation':63}]}
#                 ]
#                 if result5["query_error"] == True:
#                     return render_template("team_register.html")
#                 elif result2["error"] == True:
#                     return render_template("team_register.html", data=all_events, enroll_data=result5["query_data"])
#                 elif result2["error"] == False:
#                     api_ids = set(item["id"] for item in result2["data"])
#                     # Iterate through the event categories
#                     for category in all_events:
#                         for category_name, events in category.items():
#                             updated_events = []
#                             # Iterate through the events in the category
#                             for event in events:
#                                 event_name, event_id = list(event.keys())[0], list(event.values())[0]
#                                 # Check if the event's ID is not in the set of API IDs
#                                 if event_id not in api_ids:
#                                     updated_events.append({event_name: event_id})
#                             # Update the category with events that aren't in the API response
#                             category[category_name] = updated_events
#                     return render_template("team_register.html", data=all_events, enroll_data=result5["query_data"])
#                 else:
#                     return render_template("team_register.html")
#             except Exception as e:
#                 print("Error in solo event 2",e)
#                 return render_template("team_register.html", message="Error while connecting with database")

@app.route("/event_show", methods=["POST","GET"])
def event_show():
    url = "https://hetpatel.in/API/fetch_all_events.php"
    response= requests.get(url=url)
    result = response.json()
    data=result["data"]
    return render_template("event.html",data=data)

@app.route("/team", methods=["POST","GET"])
def team_show():
    return render_template("team.html")

# # Handlig the error code 404 with a customize html page
@app.errorhandler(404)
def page_not_found(e):
    ''' Customize page for error code 404 '''
    return render_template("error_404.html")

# Handlig the error code 500 with a customize html page
@app.errorhandler(500)
def page_not_found(e):
    ''' Customize page for error code 500 '''
    return render_template("error_500.html")

# Handling the error code 503 with a customize page
@app.errorhandler(503)
def page_not_found(e):
    ''' Customize page for error code 503 '''
    return render_template("error_503.html")

# Handling the error code 400 with a customize page
@app.errorhandler(400)
def page_not_found(e):
    ''' Customize page for error code 400 '''
    return render_template("error_400.html")
    
# Handling the error code 400 with a customize page
@app.errorhandler(504)
def page_not_found(e):
    ''' Customize page for error code 504 '''
    return render_template("error_504.html")

# For auto reload of the python

def generate_password():
    import random
    import array
    MAX_LEN = 12
    DIGITS = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    COMBINED_LIST = DIGITS 

    rand_digit = random.choice(DIGITS)

    temp_pass = rand_digit 

    for x in range(MAX_LEN - 7):
        temp_pass = temp_pass + random.choice(COMBINED_LIST)

        temp_pass_list = array.array('u', temp_pass)

        random.shuffle(temp_pass_list)

    password = ""

    for x in temp_pass_list:
        password = password + x
    return password

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
    app.run(debug=True)
    
    
    
