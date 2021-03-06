from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required

from yahtzee import db, bcrypt
from yahtzee.users.forms import (RegistrationForm, LoginForm,
                                 UpdateAccountForm, RequestResetForm,
                                 ResetPasswordForm)
from yahtzee.models import User
from yahtzee.users.utils import save_picture, send_reset_email

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')

file_handler = logging.FileHandler('yahtzee/users.log')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

# create users Blueprint instance to manage app structure
users = Blueprint('users', __name__)


@users.route("/register", methods=['GET', 'POST'])
def register():
    """
    This function responds to the browser URL localhost:5000/register
    """
    # check if user is already authenticated before presenting registration
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RegistrationForm()

    # add validate on submit to alert user if form submission successful
    if form.validate_on_submit():

        # hash password and create user from register form submission
        hashed_password = bcrypt.generate_password_hash(
                            form.password.data).decode('utf-8')

        # create user object
        user = User(
                username=form.username.data,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                password=hashed_password
                )  # passed hashed_password not plaintext form.password.data

        # try to create user in db
        try:
            db.session.add(user)
            db.session.commit()
            flash(f'Account created for {form.username.data}.', 'success')
            logger.info(f'User created: "{user}"')
        except Exception as e:
            logger.exception(f'{e}')

        # redirect user to login page
        return redirect(url_for('users.login'))  # url_for arg is route func not arg

    return render_template("register.html", title='Register', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    """
    This function responds to the browser URL localhost:5000/register
    """
    # check if user is already authenticated before presenting registration
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()

    # add validate on submit to alert user if form submission successful
    if form.validate_on_submit():

        # check if user.email exists in the db, or set user as None
        user = User.query.filter_by(email=form.email.data).first()

        # check if user and that form password matches hashed password
        if user and bcrypt.check_password_hash(user.password,
                                               form.password.data):

            # login the user with login_user method from flask_login
            login_user(user, remember=form.remember.data)

            next_page = request.args.get('next')

            return redirect(next_page) if next_page \
                else redirect(url_for('main.home'))
        else:
            flash(
                'Login unsuccessful. Please use correct email and password',
                'danger'
                )

    return render_template("login.html", title='Login', form=form)


@users.route("/logout")
def logout():
    """
    This function responds to the browser URL localhost:5000/logout
    """
    logout_user()
    return redirect(url_for('main.home'))


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    """
    This function responds to the browser URL localhost:5000/account
    """
    # create form from class
    form = UpdateAccountForm()

    # if valid form submission, update current_user attributes and flash msg
    if form.validate_on_submit():

        # log current_user data
        logger.info(f"current_user({current_user.first_name}, "
                    f"{current_user.last_name}, {current_user.username}, "
                    f"{current_user.email}, {current_user.image_file})")

        # if update form field pic, rename/save pic, and update db image_file
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
            logger.info(f"Updated {current_user.username} "
                        f"picture: {picture_file}")

        # update current_user with form field data, and commit to db
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        db.session.commit()

        # log updated current_user data
        logger.info(f"current_user({current_user.first_name}, "
                    f"{current_user.last_name}, {current_user.username}, "
                    f"{current_user.email}, {current_user.image_file})")

        flash('Account update successful', 'success')

        # redirect user to account route avoid post/redirect/get pattern issue
        return redirect(url_for('users.account'))

    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
        form.username.data = current_user.username

    image_file = url_for(
                    'static',
                    filename='profile_pics/' + current_user.image_file
                    )

    return render_template("account.html", title='Account',
                           image_file=image_file, form=form)


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():  # this func is named _request vs _password in url
    """
    This route issues a password reset token for unauthorized user email
    """
    # ensure user is not authenticated in order to reset password (vs update)
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RequestResetForm()

    # if rendered form is submitted, get user from email, send reset email
    # with token, and redirect user to the login page
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Email has been sent to reset your password', 'info')
        return redirect(url_for('users.login'))

    return render_template("reset_request.html", title='Reset Password',
                           form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):  # this func is named _token, accepts token param
    """
    This route allows user to reset password with a valid token
    """
    # ensure user is not authenticated in order to reset password (vs update)
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    # get the user_id using the verify_reset_token method and token param
    user = User.verify_reset_token(token)

    # check if user was not returned due to invalid token
    if user is None:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for('users.reset_request'))

    # if user was valid present the reset password (reset_token) form
    form = ResetPasswordForm()

    # handle password/confirm password reset form submission
    if form.validate_on_submit():

        # hash password from reset password form submission
        hashed_password = bcrypt.generate_password_hash(
                            form.password.data).decode('utf-8')

        # try to update user password in db
        try:
            user.password = hashed_password
            db.session.commit()
            flash(f'Your password has been updated.', 'success')
            logger.info(f'User created: "{user}"')
        except Exception as e:
            logger.exception(f'{e}')

        # redirect user to login page
        return redirect(url_for('users.login'))  # url_for arg is route func not arg

    return render_template("reset_token.html", title='Reset Password',
                           form=form)
