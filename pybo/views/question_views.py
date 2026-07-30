
from flask import Blueprint, render_template, url_for, redirect, request, g, flash, current_app  # flask에서 Blueprint와 render_templateㅇ르 가져온다
from pybo.models import Question, Answer, User, question_voter
from datetime import datetime
from pybo import db
from pybo.forms import QuestionForm, AnswerForm
from pybo.views.auth_views import login_required  # decorator import
from sqlalchemy import func, distinct
import os, uuid
from werkzeug.utils import secure_filename


bp = Blueprint('question', __name__, url_prefix='/question')

@bp.route('/list')
def _list():
    # 현재 페이지 번호 가져오기 (기본값은 1)
    page = request.args.get('page', type=int, default=1)
    kw = request.args.get('kw', type=str, default='')         # 검색어 keyword
    so = request.args.get('so', type=str, default='recent')   # 정렬기준

    # 1. 기본 Query
    question_list = Question.query

    # 2. 검색 (kw) 조건처리
    if kw:
        search = '%%{}%%'.format(kw)
        sub_query = (db.session.query(Answer.question_id, Answer.content, User.username)
                     .join(User, Answer.user_id == User.id).subquery())

        question_list = (question_list
                .outerjoin(sub_query, sub_query.c.question_id == Question.id)
                .filter(Question.subject.ilike(search) |
                    Question.content.ilike(search) |
                    sub_query.c.content.ilike(search) |
                    Question.user.has(User.username.ilike(search)) |
                    sub_query.c.username.ilike(search)))

    # 3. 정렬 (so) 및 그룹화 처리
        # 추천순 정렬
    if so == 'recommend':  
        # mapping 테이블(question_voter)을 직접 outerjoin하고, 그 안에 user_id 개수를 distinct하게 집계한다
        question_list = (question_list
                .outerjoin(question_voter, Question.id == question_voter.c.question_id)
                .group_by(Question.id)
                .order_by(func.count(distinct(question_voter.c.user_id)).desc(), Question.create_date.desc()))

        # 인기순 정렬 ( 답변수 기준)
    elif so == 'popular':
        question_list = (question_list
                .outerjoin(Answer, Answer.question_id == Question.id)
                .group_by(Question.id)
                .order_by(func.count(distinct(Answer.id)).desc(), Question.create_date.desc()))

        # 최신순 recent
    else:
        question_list = (question_list
                .group_by(Question.id)
                .order_by(Question.create_date.desc()))

    # 4. paging 및 rendering
    question_list = question_list.paginate(page=page, per_page=10)

    return render_template('question/question_list.html', 
                        question_list=question_list, 
                        page=page, 
                        kw=kw, 
                        so=so)

        # 페이징 기능이 적용된 질문 데이터 조회 (페이지당 10건)
        # question_list = Question.query.order_by(Question.create_date.desc()).paginate(page=page, per_page=10)
        # return render_template('question/question_list.html', question_list=question_list)
        # desc()은 역순으로 가져오는 함수, 즉 최신글부터 정렬한다  

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

        # print("=" * 50)
        # print('request.files :', request.files)
        # print('image.data :', form.image.data)
        # print('filename :', form.image.data.filename if form.image.data else None)
        # print('root_path :', current_app.root_path)
        # print('=' * 50)

        # 폼에서 전송된 이미지 파일 (다중 이미지 업로드)
        image_files = form.image.data
        image_paths = []
        # 1개 이미지 업로드
        # image_file = form.image.data
        # image_path = None
        

        # if image_file:
        #     # 저장 경로 : 오늘 날짜로 폴더 생성
        #     today = datetime.now().strftime('%Y%m%d')
        #     upload_folder = os.path.join(current_app.root_path, 'static/photo', today)
        #     os.makedirs(upload_folder, exist_ok=True)

        #     # 파일 저장
        #     # secure_filename() : 사용자가 업로드한 파일명을 운명체제에 안전하게 사용할 수 있는 형태로 반환하여, 경로 조작(Path Traversal) 등의 보안 위험을 줄여주는 함수
        #     filename = secure_filename(image_file.filename)
        #     #출력해서 만들어진 파일이름을 확인합니다.
        #     print('filename ====>', filename)

        #     ext = os.path.splitext(image_file.filename)[1]
        #     filename = f'{uuid.uuid4()}{ext}'

        #     file_path = os.path.join(upload_folder, filename)
        #     image_file.save(file_path)

        #     # DB에 저장할 경로 (static 기준 상대경로)
        #     image_path = f'photo/{today}/{filename}'

        # 저장 경로 : 오늘 날짜로 폴더 설정
        today = datetime.now().strftime('%Y%m%d')
        upload_folder = os.path.join(current_app.root_path, 'static/photo', today)
        os.makedirs(upload_folder, exist_ok=True)

        if image_files:
            for image_file in image_files:
                # 파일이 실제로 비어있지 않은지 확인
                if image_file and image_file.filename != '':
                    ext = os.path.splitext(image_file.filename)[1]
                    filename = f'{uuid.uuid4()}{ext}'
                    # filename = secure_filename(image_file.filename)
                    file_path = os.path.join(upload_folder, filename)
                    image_file.save(file_path)

                    # DB용 상대 경로 리스트에 추가
                    image_paths.append(f'photo/{today}/{filename}')
        # 여러 경로를 하나의 문자열로 합침 (예 : "path1, path2")
        # DB의 image_path column의 여러 경로를 담을 수 있을 만큼 길어야 한다
        joined_image_paths = ",".join(image_paths) if image_paths else None
        # ----

        question = Question(subject=form.subject.data, 
                            content=form.content.data, 
                            create_date=datetime.now(), 
                            user=g.user,
                            image_path=joined_image_paths)
                            # image_path=image_path)
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

