from flask import Flask
from config import Config     # has all the environment variables
from extensions import db, migrate, jwt, bcrypt
from extensions import jwt, jwt_blocklist



def create_app():
    app = Flask(__name__)    
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)


    @jwt.token_in_blocklist_loader    
    def check_if_token_revoked(jwt_header, jwt_payload: dict):
        jti = jwt_payload["jti"]  # unique identifier for the token
        return jti in jwt_blocklist   

    return app

app = create_app()

if __name__ == "__main__":

    app.run(debug=True)

