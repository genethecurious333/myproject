
from flask import Blueprint, render_template, url_for, redirect, request, g, flash  # flask에서 Blueprint와 render_templateㅇ르 가져온다
from pybo.models import Question
from datetime import datetime
from pybo import db
from pybo.forms import QuestionForm, AnswerForm
from pybo.views.auth_views import login_required  # decorator import

bp = Blueprint('question', __name__, url_prefix='/question')

@bp.route('/list')
def _list():
    # 현재 페이지 번호 가져오기 (기본값은 1)
    page = request.args.get('page', type=int, default=1)
    # 페이징 기능이 적용된 질문 데이터 조회 (페이지당 10건)
    question_list = Question.query.order_by(Question.create_date.desc()).paginate(page=page, per_page=10)
    # desc()은 역순으로 가져오는 함수, 즉 최신글부터 정렬한다
    return render_template('question/question_list.html', question_list=question_list)

@bp.route('/detail/<int:question_id>')
def detail(question_id):
    form = AnswerForm()    # 상세 조회 라우터 내부에서 빈 답변 폼 생성
    question = Question.query.get_or_404(question_id)
    return render_template('question/question_detail.html', question=question, form=form)

# 질문 등록 라우트 함수 추가
@bp.route('/create/', methods=('GET', 'POST'))
@login_required
def create():
    form = QuestionForm()
    if request.method == 'POST' and form.validate_on_submit():
        question = Question(subject=form.subject.data, content=form.content.data, create_date=datetime.now(), user=g.user)
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('question._list'))
    return render_template('question/question_form.html', form=form)

@bp.route('/modify/<int:question_id>/', methods=('GET', 'POST'))
@login_required
def modify(question_id):
    question = Question.query.get_or_404(question_id)
    if g.user != question.user:
        flash('수정권한이 없습니다')
        return redirect(url_for('question.detail', question_id=question_id))

    if request.method == 'POST':
        form = QuestionForm()
        if form.validate_on_submit():
            form.populate_obj(question)   # Form 데이터를 question 객체에 동적 복사
            db.session.commit()
            return redirect(url_for('question.detail', question_id=question_id))
    else:
        # GET 요청일 경우 기존 데이터를 폼에 채워서 rendering
        form = QuestionForm(obj=question)
    return render_template('question/question_form.html', form=form)

# 질문 삭제 처리
@bp.route('/delete/<int:question_id>/')
@login_required
def delete(question_id):
    question = Question.query.get_or_404(question_id)
    if g.user != question.user:
        flash('삭제권한이 없습니다')
        return redirect(url_for('question.detail', question_id=question_id))
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for('question._list'))

# GET 방식은 3가지, 첫째 <a> anchor tag를 적용할때, 둘째 Url에 직접 입력할때, 셋째 form tag에서 Method='GET'이라고 할때, Method생략시에도 GET방식임
# POST방식은 form tag에서 Method='POST'일때만 POST방식임

# 질문 추천 라우팅 함수
@bp.route('/vote/<int:question_id>/')
@login_required
def vote(question_id):
    question = Question.query.get_or_404(question_id)

    # 로그인한 사용자가 본인의 글을 추천하는 것을 막음
    if g.user == question.user:
        flash('본인이 작성한 글은 추천할수  없습니다')
        return redirect(url_for('question.detail', question_id=question_id))

    # 중복 추천 방지 로직
    if g.user in question.voter:
        flash('이미 추천한 질문입니다')
        return redirect(url_for('question.detail', question_id=question_id))

    # 기존 추천 처리 조직
    question.voter.append(g.user)
    db.session.commit()

    return redirect(url_for('question.detail', question_id=question_id))
