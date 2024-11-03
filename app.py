from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests

app = Flask(__name__)

app.secret_key = r"UkWJOv1eE5D089dB6AR"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///posts.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"MenuItem('{self.name}', '{self.price}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)

    def repr(self):
        return f"Post('{self.title}', '{self.date_posted}')"


API_KEY = "25f5388b3415282b4f428c7273effef0"
CITY = "Lytsk"
API_URL = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric&lang=uk"

pizza_menu = [
    {
        "name": "Маргарита",
        "ingredients": "Томати, Моцарела, Базилік",
        "price": 8.99,
    },
    {
        "name": "Пепероні",
        "ingredients": "Пепероні, Моцарела, Томатний соус",
        "price": 9.99,
    },
    {
        "name": "Барбекю з куркою",
        "ingredients": "Курка, Соус BBQ, Червона цибуля, Моцарела",
        "price": 11.99,
    },
    {
        "name": "Гавайська",
        "ingredients": "Шинка, Ананас, Моцарела, Томатний соус",
        "price": 10.99,
    },
    {
        "name": "Вегетаріанська",
        "ingredients": "Болгарський перець, Гриби, Оливки, Цибуля, Моцарела",
        "price": 9.99,
    },
]


def get_weather():
    try:
        response = requests.get(API_URL)
        data = response.json()

        if response.status_code == 200:
            weather = {
                "temp": data["main"]["temp"],
                "description": data["weather"][0]["description"],
                "city": data["name"],
            }
            return weather
        else:
            return None
    except Exception as e:
        print(f"Error occurred: {e}")
        return None


def recommend_pizza(temp, weather_desc):
    recommendation = ""

    if temp > 25:
        recommendation = (
            "Сьогодні гаряче! Рекомендуємо легку піцу з овочами та свіжим салатом."
        )
    elif temp > 15:
        recommendation = "Чудова погода! Спробуйте піцу з куркою та грибами."
    elif temp > 5:
        recommendation = "Трохи прохолодно. Рекомендуємо піцу з сиром та пепероні."
    else:
        recommendation = "Cold! Ідеально для піци з подвійним сиром та салямі."

    if "дощ" in weather_desc:
        recommendation += " А якщо йде дощ, додайте піцу з гострим соусом!"
    elif "сніг" in weather_desc:
        recommendation += " А якщо падає снігок, радимо гарячу піцу з беконом і сиром."

    return recommendation


@app.route("/")
def index():
    posts = Post.query.all()
    return render_template("posts.html", posts=posts)


@app.route("/new", methods=["GET", "POST"])
def new_post():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        new_post = Post(title=title, content=content)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("new_post.html")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_post(id):
    post = Post.query.get_or_404(id)
    if request.method == "POST":
        post.title = request.form["title"]
        post.content = request.form["content"]
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("edit_post.html", post=post)


@app.route("/delete/<int:id>", methods=["POST"])
def delete_post(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/weather")
def weather():
    weather = get_weather()
    if weather:
        temp = weather["temp"]
        description = weather["description"]
        pizza_recommendation = recommend_pizza(temp, description)
        return render_template(
            "weather.html", weather=weather, recommendation=pizza_recommendation
        )
    else:
        return "<h1>Не вдалося отримати дані про погоду.</h1>"


@app.route("/menu")
def menu():
    menu_items = MenuItem.query.all()
    return render_template("menu.html", pizzas=pizza_menu, menu_items=menu_items)


@app.route("/about")
def about():
    return render_template("about.html")


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
