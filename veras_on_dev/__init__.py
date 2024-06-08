import os
from flask import Flask, url_for

from . import db
from . import auth
from . import blog

def create_app( test_config = None ):
    # Create and configure the app
    app = Flask( __name__, instance_relative_config = True )
    app.config.from_mapping(
        SECRET_KEY = 'dev',
        DATABASE = os.path.join( app.instance_path, 'veras_on_dev.sqlite' )
    )

    if test_config is None:
        # Load the instance config if it exists when not testing
        app.config.from_pyfile( 'config.py', silent = True )
    else:
        # Load the test config if passed in
        app.config.from_mapping( test_config )

    # Ensure the instance folder exists
    try:
        os.makedirs( app.instance_path )
    except OSError:
        pass

    # A simple page that says hello

    @app.route( '/hello' )
    def hello():
        return "Hello, World!"
    
    db.init_app( app )

    app.register_blueprint( auth.bp )
    app.register_blueprint( blog.bp )

    app.add_url_rule( '/', endpoint = 'index' )

    return app