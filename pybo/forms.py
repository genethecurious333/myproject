from flask_wtf import FlaskForm 
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, PasswordField, EmailField
from wtforms.validators import DataRequired, EqualTo, Email, Length


class QuestionForm(FlaskForm):
    subject = StringField('제목', validators=[DataRequired('제목은 필수 입력입니다.')])
    content = TextAreaField('내용', validators=[DataRequired('내용은 필수 입력입니다.')])
    image = FileField('이미지 업로드',
                      validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'],
                      '이미지 파일만 업로드 가능합니다.')])

# 답변 검증용 폼 클래스 추가
class AnswerForm(FlaskForm):
    content = TextAreaField('내용', validators=[DataRequired('내용은 필수 입력 항목입니다.')])

class UserCreateForm(FlaskForm):
    username = StringField('사용자 이름', validators=[DataRequired(), Length(min=3, max=25)])
    password1 = PasswordField('비밀번호', validators=[DataRequired(), EqualTo('password2', message='비밀번호가 일치하지 않습니다.')])
    password2 = PasswordField('비밀번호 확인', validators=[DataRequired()])
    email = EmailField('이메일', validators=[DataRequired(), Email()])

# 로그인 form class 
class UserLoginForm(FlaskForm):
    username = StringField('사용자 이름', validators=[DataRequired()])
    password = PasswordField('비밀번호', validators=[DataRequired()])

# 댓글 등록 form class 
class CommentForm(FlaskForm):
    content = TextAreaField('내용', validators=[DataRequired('내용은 필수 입력 항목입니다.')])
