from flask import render_template, Blueprint
from yahtzee.models import User

main = Blueprint('main', __name__)

# create URL route in application for home "/"
@main.route("/")
@main.route("/home")
def home():
    """
    This function responds to the browser URL localhost:5000/

    return:         the rendered template "home.html"
    """
    users = User.query \
        .order_by(User.last_name) \
        .all()

    return render_template("home.html", users=users)


@main.route("/about")
def about():
    """
    This function responds to the browser URL localhost:5000/about

    return:         the renedered template "about.html"
    """
    return render_template("about.html", title='About')
