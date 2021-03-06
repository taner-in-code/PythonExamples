from functools import wraps
from flask import render_template, flash, redirect, url_for, session
from passlib.hash import sha256_crypt

class Auth():
    def __init__(self):
        pass

    def register(form, RequestMethod, dbObject):
        if RequestMethod == "POST" and form.validate():

            name = form.name.data
            username = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt(form.password.data)
            cursor = dbObject.connection.cursor()

            cursor.execute("INSERT into users(name, email, username, password) VALUES(%s, %s, %s, %s)",
                           (name, email, username, password))
            dbObject.connection.commit()
            cursor.close()

            flash("Successfuly : Register complate ...", "success")
            return redirect(url_for("login"))
        else:
            return render_template("register.html", form=form)

    def Login(form, RequestMethod, dbObject):
        if RequestMethod == "POST" and form.validate():
            username = form.username.data
            password = form.password.data

            cursor = dbObject.connection.cursor()
            result = cursor.execute("SELECT * FROM users WHERE username = %s", (username,))

            if result > 0:
                data = cursor.fetchone()
                real_password = data['password']

                if sha256_crypt.verify(password, real_password):
                    flash("Success : Login Successfuly..", "success")

                    session["logged_in"] = True
                    session["username"] = username
                    return redirect(url_for("home"))
                else:
                    flash("Error : Password not matched !", "danger")
                    return redirect(url_for("login"))

            else:
                flash("Error : User Not Found !", "danger")
                return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", form=form)

    def Logout():
        session.clear()
        flash("Info : Logout Successfully..", "info")
        return redirect(url_for("home"))

    def isLogginRequired(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):

            if "logged_in" in session:
                return f(*args, **kwargs)
            else:
                flash("Error: Permission Denied !", "danger")
                return redirect(url_for("login"))

        return decorated_function