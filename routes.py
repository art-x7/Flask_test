from config import Config

from flask import render_template, request, redirect, Blueprint, session
from forms import LoginForm, TppConfigForm, TppConfigUpdate
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash


app_routes = Blueprint("app_routes", __name__)

# Основная страница
@app_routes.route('/main', methods=["POST", "GET"])
@login_required
def index():
    from main import db
    from models import Tpp, Tpp_config

    data_product = db.session.query(Tpp_config.prod_name).all()
    product_list = {i[0] for i in data_product}

    data_process = db.session.query(Tpp.process_id).all()
    process_list = {i[0] for i in data_process}

    product = [""][0]
    resume = []
    sum_qty = [None, None]
    if request.method == "POST":
        process = request.form['list_process']
        tpp_stage = request.form['list_tpp_stage']
        prod_name = request.form['list_product']

        resume_params = {'prod_name': prod_name, 'tpp_stage': tpp_stage}
        query = f"SELECT SUM(qty_in), SUM(qty_out) FROM tpp WHERE prod_name='{prod_name}' AND tpp_stage='{tpp_stage}'"
        if process != "":
            resume_params = resume_params.update({'process': process})
            query = query + f" AND process='{process}'"
        resume = db.session.query(Tpp).filter_by(**resume_params).all()
        sum_qty = db.engine.execute(query).all()[0]
        product = prod_name
        
    return render_template('index.html', resume=resume, sum_qty=sum_qty, process_list=process_list, product=product, product_list=product_list)


# Вход/выход
@app_routes.route('/', methods=['GET', 'POST'])
def login():
    from models import User

    if current_user.is_authenticated:
        return redirect('/main')
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            return redirect('/')
        login_user(user, remember=form.remember_me.data)
        return redirect('/main')
    return render_template('login.html', form=form)


@app_routes.route('/logout')
def logout():
    logout_user()
    return redirect('/')

# Проверка допустимого расширения для загрузки файла
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in Config.ALLOWED_EXTENSIONS

# разделение строки
def split_string_prod_name(string):
    prod_name = string[:string.find("ТПП") - 1]
    return prod_name

def split_string_numb(string):     
    tpp_splitted = string.split()
    numb = tpp_splitted[-1].strip("(").strip("№").strip(")")
    return numb

def split_string_tpp_stage(string):     
    tpp_splitted = string.split()
    if "единичных" in tpp_splitted:
        tpp_stage = "ТПП единичных изделий"
    else:
        tpp_stage = "ТПП серийных изделий" 
    return tpp_stage

# Страница для заполнения отчета
@app_routes.route('/form', methods=["POST", "GET"])
@login_required
def input_form_page():
    from main import db
    from models import Tpp, Tpp_config, Materials, Process

    materials_choice = db.session.query(Materials).all()
    tpp_config = db.session.query(Tpp_config).filter_by(status="Открыт", del_status=True).all()
    process = db.session.query(Process).all()
    if request.method == "POST":
        prod_sum = request.form['prod_name']
        process = request.form['process_name']
        tpp_stage = split_string_tpp_stage(prod_sum)
        prod_name = split_string_prod_name(prod_sum)
        tpp_numb = split_string_numb(prod_sum)
        prod_id = db.session.query(Tpp_config).filter_by(tpp_stage=tpp_stage, prod_name=prod_name, tpp_numb=tpp_numb).first()
        lot_name = request.form['lot_name']
        qty_in = request.form['qty_in']
        qty_out = request.form['qty_out']
        defects = request.form['defects']
        materials = request.form['materials']
        volume_materials = request.form['volume_materials']
        equipment = request.form['equipment']
        tool_name = request.form['tool_name']
        recipe = request.form['recipe']
        time_s = request.form['time_s']
        time_p = request.form['time_p']
        uph = request.form['uph']
        wafer_name = request.form['wafer_name']
        warpage = request.form['warpage']
        willingness = request.form['willingness']
        comment = request.form['comment']
        risk = request.form['risk']
        user_id = current_user.id
        tpp = Tpp(process=process,
                prod_id=prod_id,
                tpp_stage=tpp_stage,
                tpp_numb=tpp_numb,
                lot_name=lot_name,
                qty_in=qty_in,
                qty_out=qty_out,
                defects=defects,
                materials=materials,
                volume_materials=volume_materials,
                equipment=equipment,
                tool_name=tool_name,
                recipe=recipe,
                time_s=time_s,
                time_p=time_p,
                uph=uph,
                wafer_name=wafer_name,
                warpage=warpage,
                willingness=willingness,
                comment=comment,
                risk=risk,
                user_id=user_id)

        try:
            db.session.add(tpp)
            db.session.commit()
            return redirect('/main')
        except:
            return "При добавление произошла ошибка"

    return render_template('form_for_tpp/form.html', tpp_config=tpp_config, materials_choice=materials_choice, process=process)


# Страница для конфигурирования ТПП
@app_routes.route('/config_tpp', methods=["POST", "GET"])
@login_required
def config_tpp():
    from main import db
    from models import Tpp_config
    
    form = TppConfigForm()
    tpp_config = db.session.query(Tpp_config).filter_by(del_status=True).all()
        
    if form.validate_on_submit():
        product = Tpp_config.query.filter_by(prod_name=form.prod_name.data, tpp_stage = form.tpp_stage.data, number=form.tpp_numb.data).first()
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

    return render_template('config_folder/config_tpp.html', form=form, tpp_config=tpp_config)


# Изменение записи Tpp_config
@app_routes.route('/update/<int:id>', methods=["POST", "GET"])
@login_required
def update_config_tpp(id):
    from main import db
    from models import Tpp_config

    form = TppConfigUpdate()

    data_product = db.session.query(Tpp_config).filter_by(id=id).all()
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
            return redirect('/config_tpp')
        except:
            return "При обновлении произошла ошибка"
    return render_template('config_folder/update.html', data_product=data_product, form=form)


# Удаление записи Tpp_config
@app_routes.route('/delete/<int:id>', methods=["POST", "GET"])
@login_required
def delete_config_tpp(id):
    from main import db
    from models import Tpp_config
  
    product_to_delete = Tpp_config.query.get_or_404(id)
    product_to_delete.del_status = False
    try:
        db.session.commit()  
        return redirect('/config_tpp')
    except:
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

    return render_template('config_folder/config_user.html', users=users)


# добавление оборудования
@app_routes.route('/add_materials', methods=["POST", "GET"])
def add_materials():
    from main import db
    from models import Materials, Process

    materials = db.session.query(Materials).all()
    process = db.session.query(Process).all()

    if request.method == "POST":
        process_name = request.form['process']
        material_name = request.form['material']
        unit = request.form['unit']
        process_id = db.session.query(Process.id).filter_by(process=process_name).all()[0][0]
      
        check_process = Materials.query.filter_by(material=material_name).first()
  
        if check_process is None:
            add_material = Materials(process_id=process_id, material=material_name, unit=unit)
        
            try:
                db.session.add(add_material)
                db.session.commit()
                return redirect('/add_materials')
            except:
                return "При добавление произошла ошибка"
    return render_template('config_folder/add_materials.html', materials=materials, process=process)


# добавление процесса
@app_routes.route('/add_process', methods=["POST", "GET"])
def add_process():
    from main import db
    from models import Process

    process = db.session.query(Process).all()
    if request.method == "POST":
        new_process = request.form['add_process']
        check_process = Process.query.filter_by(process=new_process).first()
        
        if check_process is None:
            add_process = Process(process=new_process)
        
            try:
                db.session.add(add_process)
                db.session.commit()
                return redirect('/add_process')
            except:
                return "При добавление произошла ошибка"
    
    return render_template('config_folder/add_process.html', process=process)    


# добавление обоудования
@app_routes.route('/add_equipment', methods=["POST", "GET"])
def add_equipment():
    from main import db
    from models import Equipment, Process

    equipments = db.session.query(Equipment).all()
    process = db.session.query(Process).all()

    if request.method == "POST":
        process_name = request.form['process']
        equipment = request.form['equipment']
        
        process_id = db.session.query(Process.id).filter_by(process=process_name).all()[0][0]
      
        check_equipment = Equipment.query.filter_by(main=equipment).first()
  
        if check_equipment is None:
            add_equipment = Equipment(process_id=process_id, main=equipment)
            try:
                db.session.add(add_equipment)
                db.session.commit()
                return redirect('/add_equipment')
            except:
                return "При добавление произошла ошибка"
                
    return render_template('config_folder/add_equipment.html', equipments=equipments, process=process)


# добавление оснастки
@app_routes.route('/add_tool', methods=["POST", "GET"])
def add_tool():
    from main import db
    from models import Equipment, Process, Tool

    equipments = db.session.query(Equipment).all()
    process = db.session.query(Process).all()
    tools = db.session.query(Tool).all()

    if request.method == "POST":
        equipment_name = request.form['equipment']
        tool = request.form['tool']
        
        equipment_id = db.session.query(Equipment.id).filter_by(main=equipment_name).all()[0][0]
      
        check_equipment = Tool.query.filter_by(tool=tool).first()
  
        if check_equipment is None:
            add_tool = Tool(tool=tool, equipment_id=equipment_id)
            try:
                db.session.add(add_tool)
                db.session.commit()
                return redirect('/add_tool')
            except:
                return "При добавление произошла ошибка"
                
    return render_template('config_folder/add_tool.html', equipments=equipments, process=process, tools=tools)

# Страница для 404 ошибки
@app_routes.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', error=error), 404
