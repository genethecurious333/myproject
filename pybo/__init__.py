
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from pybo.filter import format_datetime

import config 

db = SQLAlchemy()
migrate = Migrate()

# application factory 함수 정의
def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    # ORM 초기화, 데이터 베이스 준비
    from . import models
    db.init_app(app)
    migrate.init_app(app, db)

    # jinja_env filter에 등록
    app.jinja_env.filters['datetime'] = format_datetime

    # Blueprint 등록
    from .views import main_views, question_views, answer_views, auth_views, comment_views
    app.register_blueprint(main_views.bp)
    app.register_blueprint(question_views.bp)
    app.register_blueprint(answer_views.bp)
    app.register_blueprint(auth_views.bp)   # 회원가입 등록
    app.register_blueprint(comment_views.bp)
    
    return app