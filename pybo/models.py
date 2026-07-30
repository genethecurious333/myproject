
from pybo import db 
from sqlalchemy import Table

# 중간 테이블 정의, 추천기능에 적용
question_voter = Table(
    'question_voter',
    db.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('question_id', db.Integer, db.ForeignKey('question.id', ondelete='CASCADE'), primary_key=True)
)

answer_voter = Table(
    'answer_voter',
    db.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('answer_id', db.Integer, db.ForeignKey('answer.id', ondelete='CASCADE'), primary_key=True)
)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True) # id를 주면 이것이 기본키가 된다는 의미
    subject = db.Column(db.String(200), nullable=False) # nullable=False는 값이 꼭들어가야한다는 의미, 200자까지 작성가능
    content = db.Column(db.Text(), nullable=False)
    create_date = db.Column(db.DateTime(), nullable=False) # 작성 일자
    # 업로드된 이미지 경로 추가
    image_path = db.Column(db.String(200), nullable=True)
    # 글쓴이 author 외래키 및 관계 설정 추가 (기존 데이터 고려 nullable=True 우선 허용)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=True, server_default='1')
    user = db.relationship('User', backref=db.backref('question_set'))
    # 추천인 (다대다 N:N)
    voter = db.relationship(
        'User',                         # 추천한 사용자(User) 모델과 연결
        secondary=question_voter,       # 다대다 관계를 위한 중간 테이블(question_voter) 사용
        backref=db.backref('quesiton_voter_set',    # User 객체에서 추천한 질문 목록을 조회하는 속성
                           lazy='dynamic'           # 실제 조회 시점에 SQL을 실행하여 Query 객체를 반환
                           ))
class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id', ondelete='CASCADE')) # Question이 지워지면 Answer도 delete하라. Answer는 Question과 같은 번호를 가지고 있어야함.
    question = db.relationship('Question', backref=db.backref('answer_set', cascade='all, delete-orphan'))
    content = db.Column(db.Text(), nullable=False)
    create_date = db.Column(db.DateTime(), nullable=False)
    # 글쓴이 외래키 및 관계설정 추가
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=True, server_default='1')
    user = db.relationship('User', backref=db.backref('answer_set'))
    # 추천인 (다대다 N:N)
    voter = db.relationship('User', secondary=answer_voter, 
                            backref=db.backref('answer_voter_set', lazy='dynamic'))
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship('User', backref=db.backref('comment_set'))

    content = db.Column(db.Text(), nullable=False)
    create_date = db.Column(db.DateTime(), nullable=False)
    modify_date = db.Column(db.DateTime())
    # 질문 테이블 및 답변 테이블과의 다대일(N:1) 관계 ForeignKey Mapping
    question_id = db.Column(db.Integer, db.ForeignKey('question.id', ondelete='CASCADE'), nullable=True)
    question = db.relationship('Question', backref=db.backref('comment_set'))
    answer_id = db.Column(db.Integer, db.ForeignKey('answer.id', ondelete='CASCADE'), nullable=True)
    answer = db.relationship('Answer', backref=db.backref('comment_set'))

# Database(models.py)에서의 수정이 발생했을때는 반드시 flask db migrate와 flask db upgrade를 해준다. 
# migrate와 upgrade전에 우선 set부터 완료한다. set FLASK_APP=pybo   set FLASK-ENV=development

