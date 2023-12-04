from flask import Flask
from api.film import film_api
from api.order import order_api



app = Flask(__name__)

# Register the blueprint with the app
app.register_blueprint(film_api)
app.register_blueprint(order_api)



if __name__ == '__main__':
    app.run(debug=True)
