from flask import render_template, request, redirect, Blueprint, flash, url_for
from forms import LoginForm
from flask_login import current_user, login_user,  logout_user, login_required
from werkzeug.urls import url_parse

app_routes = Blueprint("app_routes", __name__)


# Основная страница
@app_routes.route('/', methods=["POST", "GET"])
@login_required
def index():
    from main import db
    
    data_product = db.engine.execute(f"SELECT prod_name FROM Tpp_config ORDER BY prod_name").all()
    product_list = {i[0] for i in data_product}
    data_process = db.engine.execute(f"SELECT process FROM Tpp ORDER BY process").all()
    process_list = {i[0] for i in data_process}
    
    product = [""][0]
    resume = []
    sum_qty = [None, None]
    if request.method == "POST":
        process = request.form['list_process']
        tpp_stage = request.form['list_tpp_stage']
        prod_name = request.form['list_product']

        if process == "":
            resume = db.engine.execute(f"SELECT * FROM tpp WHERE prod_name='{prod_name}' AND tpp_stage='{tpp_stage}' ORDER BY process").all()

            sum_qty = db.engine.execute(f"SELECT SUM(qty_in), SUM(qty_out) FROM tpp WHERE prod_name='{prod_name}' AND tpp_stage='{tpp_stage}'").all()[0]
        else:
            resume = db.engine.execute(f"SELECT * FROM tpp WHERE prod_name='{prod_name}' AND tpp_stage='{tpp_stage}' AND process='{process}'").all()

            sum_qty = db.engine.execute(f"SELECT SUM(qty_in), SUM(qty_out) FROM tpp WHERE prod_name='{prod_name}' AND tpp_stage='{tpp_stage}' AND process='{process}'").all()[0]
        

        product = prod_name

    return render_template('index.html', resume=resume, sum_qty=sum_qty, process_list=process_list, product=product, product_list=product_list)


# Страница для входа
@app_routes.route('/login', methods=['GET', 'POST'])
def login_page():
    from models import User
    
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect('/login')
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(url_for('next_page'))

    return render_template('login.html', form=form)

@app_routes.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# Страница для заполнения отчета
@app_routes.route('/form', methods=["POST", "GET"])
def input_form_page():
    from main import db
    from models import Tpp

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

        tpp = Tpp(
            process=process,
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
            comment=comment
        )

        try:
            db.session.add(tpp)
            db.session.commit()
            return redirect('/')
        except:
            return "При добавление произошла ошибка"

    else:
        return render_template('form_for_tpp/form.html')


# Страница для конфигурирования ТПП
@app_routes.route('/config_page', methods=["POST", "GET"])
def config_page():
    from main import db
    from models import Tpp_config
    
    tpp_config = db.session.query(Tpp_config).all()
    if request.method == "POST":
        if request.form["btn"] == "add":
            prod_name = request.form['master_add_product']
            tpp_stage = request.form['master_add_tpp_stage']
            number = request.form['master_add_number']
            owner = request.form['master_add_owner']
            comment = request.form['master_comment']

            config_product = Tpp_config(
                prod_name=prod_name,
                tpp_stage=tpp_stage,
                number=number,
                owner=owner,
                comment=comment
            )

            try:
                db.session.add(config_product)
                db.session.commit()
                return redirect('/config_page')
            except:
                return "При добавление произошла ошибка"
        elif request.form["btn"] == "update":
            id_tabel = request.form["up_table_id"]
            prod_name_table = request.form['up_table_prod_name']
            tpp_stage_table = request.form['up_table_tpp_stage']
            number_table = request.form['up_table_number']
            owner_table = request.form['up_table_owner']
            comment_table = request.form['up_table_comment']
        
            new_prod_name = Tpp_config.query.get(id_tabel)
            print(comment)
            try:              
                new_prod_name.prod_name = prod_name_table
                new_prod_name.tpp_stage = tpp_stage_table
                new_prod_name.number = number_table
                new_prod_name.owner = owner_table 
                new_prod_name.comment = comment_table
                db.session.add(new_prod_name)
                db.session.commit()
                return redirect('/config_page')
            except:
                return "При изменении произошла ошибка"

    else:
        return render_template('config_page.html', tpp_config=tpp_config)

# Страница обновления Tpp_config
@app_routes.route('/update_page', methods=["POST", "GET"])
def update_config():
    from main import db
    from models import Tpp_config
    tpp_config = db.session.query(Tpp_config).all()
    
    if request.method == "POST":
        id_change = request.form["change_id"]
        prod_name = request.form["change_product"]
        tpp_stage = request.form["change_tpp_stage"]
        number = request.form["change_number"]
        owner = request.form["change_owner"]
        comment = request.form["change_comment"]

        new_prod_name = Tpp_config.query.get(id_change)
   
        try:              
            new_prod_name.prod_name = prod_name
            new_prod_name.tpp_stage = tpp_stage 
            new_prod_name.number = number
            new_prod_name.owner = owner 
            new_prod_name.comment = comment
            db.session.add(new_prod_name)
            db.session.commit()
            return redirect('/config_page')
        except:
            return "При изменении произошла ошибка"
    else:   
        return render_template('config_update.html', tpp_config=tpp_config)



# Страница для 404 ошибки
@app_routes.errorhandler(404)
def page_not_found(error):
    return render_template('page404.html')
