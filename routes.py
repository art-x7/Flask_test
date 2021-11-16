from flask import render_template, request, redirect, Blueprint, flash, session
from forms import LoginForm, TppConfigForm, TppConfigUpdate
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename

from config import Config


app_routes = Blueprint("app_routes", __name__)


# Основная страница
@app_routes.route('/', methods=["POST", "GET"])
def index():
    from main import db

    data_product = db.engine.execute(
        f"SELECT prod_name FROM Tpp_config ORDER BY prod_name").all()
    product_list = {i[0] for i in data_product}
    data_process = db.engine.execute(
        f"SELECT process FROM Tpp ORDER BY process").all()
    process_list = {i[0] for i in data_process}

    product = [""][0]
    resume = []
    sum_qty = [None, None]
    if request.method == "POST":
        process = request.form['list_process']
        tpp_stage = request.form['list_tpp_stage']
        prod_name = request.form['list_product']
        
        if process == "":
            resume = db.engine.execute(
                f"SELECT * FROM tpp WHERE prod_name='{prod_name}' AND tpp_stage='{tpp_stage}' ORDER BY id"
            ).all()

            sum_qty = db.engine.execute(
                f"SELECT SUM(qty_in), SUM(qty_out) FROM tpp WHERE prod_name='{prod_name}' AND tpp_stage='{tpp_stage}'"
            ).all()[0]
        else:
            resume = db.engine.execute(
                f"SELECT * FROM tpp WHERE prod_name='{prod_name}' AND tpp_stage='{tpp_stage}' AND process='{process}'"
            ).all()

            sum_qty = db.engine.execute(
                f"SELECT SUM(qty_in), SUM(qty_out) FROM tpp WHERE prod_name='{prod_name}' AND tpp_stage='{tpp_stage}' AND process='{process}'"
            ).all()[0]

        product = prod_name
    
    return render_template('index.html', resume=resume, sum_qty=sum_qty, process_list=process_list, product=product, product_list=product_list)


# Страница для входа
@app_routes.route('/login', methods=['GET', 'POST'])
def login():
    from models import User

    if current_user.is_authenticated:
        return redirect('/')
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            return redirect('/login')
        login_user(user, remember=form.remember_me.data)
        return redirect('/')
    return render_template('login.html', form=form)


@app_routes.route('/logout')
def logout():
    logout_user()
    return redirect('/')

# Проверка допустимого расширения для загрузки файла
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in Config.ALLOWED_EXTENSIONS


# Страница для заполнения отчета
@app_routes.route('/form', methods=["POST", "GET"])
@login_required
def input_form_page():
    from main import db
    from models import Tpp

    data_product = db.engine.execute(
                f"SELECT prod_name FROM Tpp_config WHERE status ='Открыт' ORDER BY prod_name").all()
    product_list = {i[0] for i in data_product}

    if request.method == "POST":
        process = request.form['process_name']
        tpp_stage = request.form['tpp_stage']
        prod_name = request.form['prod_name']
        lot_name = request.form['lot_name']
        q_in = request.form['qty_in']
        q_out = request.form['qty_out']
        defects = request.form['defects']
        materials = request.form['materials']
        tool_name = request.form['tool_name']
        recipe = request.form['recipe']
        time_s = request.form['time_s']
        time_p = request.form['time_p']
        uph = request.form['uph']
        wafer_name = request.form['wafer_name']
        warpage = request.form['warpage']
        info = request.form['info']
        comment = request.form['comment']
        user_id = current_user.id
        tpp = Tpp(process=process,
                tpp_stage=tpp_stage,
                prod_name=prod_name,
                lot_name=lot_name,
                qty_in=q_in,
                qty_out=q_out,
                defects=defects,
                materials=materials,
                tool_name=tool_name,
                recipe=recipe,
                time_s=time_s,
                time_p=time_p,
                uph=uph,
                wafer_name=wafer_name,
                warpage=warpage,
                info=info,
                comment=comment,
                user_id=user_id)

        try:
            db.session.add(tpp)
            db.session.commit()
            return redirect('/')
        except:
            return "При добавление произошла ошибка"

    return render_template('form_for_tpp/form.html', product_list=product_list)


# Страница для конфигурирования ТПП
@app_routes.route('/config_tpp', methods=["POST", "GET"])
@login_required
def config_tpp():
    from main import db
    from models import Tpp_config
    
    form = TppConfigForm()
    tpp_config = db.session.query(Tpp_config).all()
        
    if form.validate_on_submit():
        product = Tpp_config.query.filter_by(prod_name=form.prod_name.data, tpp_stage = form.tpp_stage.data,number=form.tpp_numb.data).first()
        if product is None:
            prod_name = form.prod_name.data
            tpp_stage = form.tpp_stage.data
            number = form.tpp_numb.data
            owner = form.prod_owner.data
            comment = form.comment.data
            new_prod = Tpp_config(prod_name=prod_name, tpp_stage=tpp_stage, number=number, owner=owner, comment=comment)
            try:
                db.session.add(new_prod)
                db.session.commit()
                return redirect('/config_tpp')
            except:
                return "При добавление произошла ошибка"

    return render_template('config_tpp.html', form=form, tpp_config=tpp_config)


# Изменение записи Tpp_config
@app_routes.route('/update/<int:id>', methods=["POST", "GET"])
def update_config_tpp(id):
    from main import db
    from models import Tpp_config

    form = TppConfigUpdate()
    data_product = db.engine.execute(
        f"SELECT * FROM Tpp_config WHERE id={id}").all()
       
    product_to_update = Tpp_config.query.get_or_404(id)
    if request.method == "POST":
        product_to_update.prod_name = request.form["prod_name"]
        product_to_update.tpp_stage = request.form["tpp_stage"]
        product_to_update.number = request.form["tpp_numb"]
        product_to_update.owner = request.form["prod_owner"]
        product_to_update.comment = request.form["comment"]
        product_to_update.status = request.form["status"]
        try:
            db.session.commit()
            flash("Product Update Successfully!")
            return redirect('/config_tpp')
        except:
            flash("Product Not Updated!")
    return render_template('update.html', data_product=data_product, form=form)


# Удаление записи Tpp_config
@app_routes.route('/delete/<int:id>', methods=["POST", "GET"])
def delete_config_tpp(id):
    from main import db
    from models import Tpp_config
  
    product_to_delete = Tpp_config.query.get_or_404(id)
    try:
        db.session.delete(product_to_delete)
        db.session.commit()
        flash("Product Deleted Successfully!")
        return redirect('/config_tpp')
    except:
        flash("Product Not Deleted!")
        return "При удаление произошла ошибка"
    

# Страница обновления config_user
@app_routes.route('/config_user', methods=["POST", "GET"])
def config_user():
    from main import db
    from models import User
    users = db.session.query(User).all()
    if request.method == "POST":
        session.pop('_flashes', None)
        if len(request.form['user_login']) > 4 and len(request.form['user_email']) > 4 \
                and len(request.form['user_pass']) > 4 and request.form['user_pass'] == request.form['user_pass2']:
            hash_psw = generate_password_hash(request.form['user_pass'])
            user_config = User(login=request.form['user_login'], email=request.form['user_email'], password_hash=hash_psw)
            try:
                db.session.add(user_config)
                db.session.commit()
                return redirect('/config_user')
            except:
                return "При добавление произошла ошибка"

    return render_template('config_user.html', users=users)


# Страница для 404 ошибки
@app_routes.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', error=error), 404
