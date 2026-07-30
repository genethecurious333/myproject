
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from pybo.filter import format_datetime
import markdown
from markupsafe import Markup
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

    # 1. 마크다운 변환 함수를 선언한다
    def format_markdown(text):
        if not text:
            return ""

        # markdown.markdown()의 결과(문자열)를 MarkupSafe의 Markup 객체로 감싸줍니다.
        # 이렇게 감싸주어야 템플릿(HTML)에서 꺾쇠 태그가 무력화되지 않고 화면에 잘 나온다
        html_content = markdown.markdown(text, extensions=['nl2br', 'fenced_code', 'sane_lists', 'tables'])

        # Bootsrap 클래스 추가
        html_content = html_content.replace(
            '<table>',
            '<table class="table table-bordered table-hover">'
        )

        return Markup(html_content)

    # 2. Flask 앱의 Jinja2 템플릿 필터로 등록한다. (필터 이름: 'markdown')
    app.jinja_env.filters['markdown'] = format_markdown

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

