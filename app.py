from flask import Flask
from config import Config     # has all the environment variables
from extensions import db, migrate, jwt, bcrypt
from extensions import jwt, jwt_blocklist


def create_app():     # factory function jo flask app create krte h
    app = Flask(__name__)    
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)    # connecting database and app
    migrate.init_app(app, db)
    jwt.init_app(app)   # connecting jwt manager with the app
    bcrypt.init_app(app)   # connecting bcrypt with the app


    @jwt.token_in_blocklist_loader    # ye ek jwt ka in-built callback function h jo automatically call hota h jb bhi ek user login krta h aur check krta h ki token logout hone ke baad valid h ya nhi
    def check_if_token_revoked(jwt_header, jwt_payload: dict):
        jti = jwt_payload["jti"]  # unique identifier for the token
        return jti in jwt_blocklist   # if the token id is in the blocklist means the token is invalid so the response would be true or false

    # Import blueprints
    from routes.auth import auth_bp    # ye humne isliye use kia h taki hume saara code ek hi file me na rkhna pde
    from routes.blog import blog_bp    # blueprints are for modularity(tukdo me code rkhna) and scalability(jese jese app bdi hoti h routes add krne m asaani hoti h)

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(blog_bp, url_prefix="/blog")

    return app

if __name__ == "__main__":
    app = create_app()

    # # Make sure this is **after app is created**
    # with app.app_context():
    #     db.create_all()  # creates tables if they don’t exist

    app.run(debug=True)


