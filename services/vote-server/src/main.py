from flask import Flask
from fill_database_with_dummy_data import dummy_data_fill

# to run : flask --app main run
app = Flask(__name__)
app.register_blueprint(dummy_data_fill)
