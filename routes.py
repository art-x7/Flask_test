from flask import render_template, request, redirect, Blueprint, session, send_from_directory
from forms import LoginForm, TppConfigForm, TppConfigUpdate, UpdateUph
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash
from config import Config


app_routes = Blueprint("app_routes", __name__)


# Удаление пробелов до и после текста
def del_space_string(string):
    new_string = ' '.join(string.split())
    return new_string


# Проверка допустимого расширения для загрузки файла
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in Config.ALLOWED_EXTENSIONS


@app_routes.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(Config.UPLOAD_FOLDER, filename)

# Страница для 404 ошибки
@app_routes.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', error=error)


# Основная страница
@app_routes.route('/main', methods=["POST", "GET"])
@login_required
def index():
    from main import db
    from models import Tpp, Tpp_config, Process, User, Materials, Equipment, Tool

    tpp_config = db.session.query(Tpp_config).filter_by(status="Открыт", del_status=True).all()

    data_process = db.session.query(Tpp.process_id).all()
    process_list = {i[0] for i in data_process}  
    
    process_GSN = []
    for item in process_list:
        process = db.session.query(Process).filter_by(id=item).all()[0]
        process_GSN.append(process)

    branch_footer = db.session.query(Process).group_by(Process.branch).all()
    process_footer = db.session.query(Process).all()

    title_product = [""][0]
    result = []
    sum_qty = [None, None]
    if request.method == "POST":
        prod_sum = request.form['list_product']
        process = request.form['list_process']
        prod_id = db.session.query(Tpp_config.id).filter_by(prod_sum=prod_sum).first()[0]
        
        result = db.session.query(Tpp, Process, User, Materials, Equipment, Tool).select_from(Tpp).join(Materials).join(Tool).join(Equipment).join(Process).join(User).all()

        query = f"SELECT SUM(qty_in), SUM(qty_out) FROM tpp WHERE prod_id='{prod_id}'"
        if process != "":
            process_id = db.session.query(Process.id).filter_by(process=process).first()[0]
        
            result = db.session.query(Tpp, Process, User, Materials, Equipment, Tool).select_from(Tpp).join(Materials).join(Tool).join(Equipment).join(Process).join(User).filter(Tpp.process_id == process_id, Tpp.prod_id == prod_id).all()
            query = query + f" AND process_id='{process_id}'"

        sum_qty = db.engine.execute(query).all()[0]
        title_product = prod_sum
  
    return render_template('index.html', result=result, sum_qty=sum_qty, title_product=title_product, tpp_config=tpp_config, process_GSN=process_GSN, branch_footer=branch_footer, process_footer=process_footer)


# Вход/выход
@app_routes.route('/', methods=['GET', 'POST'])
def login():
    from main import db
    from models import User

    if current_user.is_authenticated:
        return redirect('/main')
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter_by(login=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            return redirect('/')
        login_user(user, remember=form.remember_me.data)
        return redirect('/main')
    return render_template('login.html', form=form)


@app_routes.route('/logout')
def logout():
    logout_user()
    return redirect('/')



# Страница для заполнения отчета
@app_routes.route('/form', methods=["POST", "GET"])
@login_required
def input_form_page():
    from main import db
    from models import Tpp, Tpp_config, Materials, Process, Equipment, Tool

    materials_choice = db.session.query(Materials).all()
    tpp_config = db.session.query(Tpp_config).filter_by(status="Открыт", del_status=True).all()
    process_choice = db.session.query(Process).all()
    equipment_choice = db.session.query(Equipment).all()
    tool_choice = db.session.query(Tool).all()

    branch_footer = db.session.query(Process).group_by(Process.branch).all()
    process_footer = db.session.query(Process).all()

    if request.method == "POST":
        prod_sum = request.form['prod_name']
        process = request.form['process_name']
        process_id = db.session.query(Process.id).filter_by(process=process).first()[0]
        prod_id = db.session.query(Tpp_config.id).filter_by(prod_sum=prod_sum).first()[0]
        lot_name = request.form['lot_name']
        qty_in = request.form['qty_in']
        qty_out = request.form['qty_out']
        defects = request.form['defects']
        material = request.form['materials']
        materials_id = db.session.query(Materials.id).filter_by(material=material).first()[0]
        volume_materials = request.form['volume_materials']
        equipment = request.form['equipment']
        equipment_id = db.session.query(Equipment.id).filter_by(main=equipment).first()[0]
        tool_name = request.form['tool_name']
        tool_id = db.session.query(Tool.id).filter_by(tool=tool_name).first()[0]
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
       
        tpp = Tpp(process_id=process_id,
                prod_id=prod_id,
                lot_name=lot_name,
                qty_in=qty_in,
                qty_out=qty_out,
                defects=defects,
                materials_id=materials_id,
                volume_materials=volume_materials,
                equipment_id=equipment_id,
                tool_id=tool_id,
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

    return render_template('form_for_tpp/form.html', tpp_config=tpp_config, materials_choice=materials_choice, process_choice=process_choice, equipment_choice=equipment_choice, tool_choice=tool_choice, branch_footer=branch_footer, process_footer=process_footer)


# Страница для конфигурирования ТПП
@app_routes.route('/config_tpp/', methods=["POST", "GET"])
@login_required
def config_tpp():
    from main import db
    from models import Tpp_config, Process
    
    form = TppConfigForm()
    tpp_config = db.session.query(Tpp_config).filter_by(del_status=True).all()
    branch_footer = db.session.query(Process).group_by(Process.branch).all()
    process_footer = db.session.query(Process).all()

    if form.validate_on_submit():
        product = db.session.query(Tpp_config).filter_by(prod_sum=f"{str(form.prod_name.data)} {str(form.tpp_stage.data)} (№{str(form.tpp_numb.data)})").first()
        if product is None:
            prod_name = form.prod_name.data
            tpp_stage = form.tpp_stage.data
            number = form.tpp_numb.data
            prod_sum = f"{str(prod_name)} {str(tpp_stage)} (№{str(number)})"
            owner = form.prod_owner.data
            comment = form.comment.data
            new_prod = Tpp_config(prod_sum=prod_sum, owner=owner, comment=comment)
            try:
                db.session.add(new_prod)
                db.session.commit()
                return redirect('/config_tpp')
            except:
                return "При добавление произошла ошибка"

    return render_template('config_folder/config_tpp.html', form=form, tpp_config=tpp_config, branch_footer=branch_footer, process_footer=process_footer)


# Изменение записи Tpp_config
@app_routes.route('/update/<int:id>', methods=["POST", "GET"])
@login_required
def update_config_tpp(id):
    from main import db
    from models import Tpp_config, Process

    form = TppConfigUpdate()
    branch_footer = db.session.query(Process).group_by(Process.branch).all()
    process_footer = db.session.query(Process).all()

    data_product = db.session.query(Tpp_config).filter_by(id=id).all()
    product_to_update = db.session.query(Tpp_config).get_or_404(id)
    if request.method == "POST":
        product_to_update.prod_sum = request.form["prod_name"]
        product_to_update.owner = request.form["prod_owner"]
        product_to_update.comment = request.form["comment"]
        product_to_update.status = request.form["status"]
        try:
            db.session.commit()
            return redirect('/config_tpp')
        except:
            return "При обновлении произошла ошибка"
    return render_template('config_folder/update.html', data_product=data_product, form=form, branch_footer=branch_footer, process_footer=process_footer)


# Удаление записи Tpp_config
@app_routes.route('/delete/<int:id>', methods=["POST", "GET"])
@login_required
def delete_config_tpp(id):
    from main import db
    from models import Tpp_config
  
    product_to_delete = db.session.query(Tpp_config).get_or_404(id)
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
    from models import User, Process
    
    users = db.session.query(User).all()
    branch_footer = db.session.query(Process).group_by(Process.branch).all()
    process_footer = db.session.query(Process).all()

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

    return render_template('config_folder/config_user.html', users=users,branch_footer=branch_footer, process_footer=process_footer)


# добавление процесса
@app_routes.route('/add_process', methods=["POST", "GET"])
def add_process():
    from main import db
    from models import Process

    branch_footer = db.session.query(Process).group_by(Process.branch).all()
    process_footer = db.session.query(Process).all()

    process = db.session.query(Process).all()
    if request.method == "POST":
        new_process = request.form['add_process']
        branch = request.form['branch']

        check_process = db.session.query(Process).filter_by(process=del_space_string(new_process)).first()
        if check_process is None:
            add_process = Process(process=del_space_string(new_process), branch=branch)   
            try:
                db.session.add(add_process)
                db.session.commit()
                return redirect('/add_process')
            except:
                return "При добавление произошла ошибка"
    
    return render_template('config_folder/add_process.html', process=process,branch_footer=branch_footer, process_footer=process_footer)   


# Процессы (для загрузки входных данных)
@app_routes.route('/<string:process>')
@login_required
def process_all(process):
    from main import db
    from models import Process

    branch_footer = db.session.query(Process).group_by(Process.branch).all()
    process_footer = db.session.query(Process).all()

    return render_template('process.html', process=process, branch_footer=branch_footer, process_footer=process_footer)


# добавление материалов
@app_routes.route('/<string:process>/add_materials', methods=["POST", "GET"])
def add_materials(process):
    from main import db
    from models import Materials, Process

    
    branch_footer = db.session.query(Process).group_by(Process.branch).all()
    process_footer = db.session.query(Process).all()
    
    materials = db.session.query(Materials, Process).select_from(Materials).join(Process).filter(Process.process == process).all()
    

    if request.method == "POST":

        material_name = request.form['material']
        unit = request.form['unit']
        process_id = db.session.query(Process.id).filter_by(process=process).all()[0][0]
        
        check_material = db.session.query(Materials).filter_by(material=del_space_string(material_name)).first()
        if check_material is None:
            add_material = Materials(process_id=process_id, material=del_space_string(material_name), unit=del_space_string(unit))
            try:
                db.session.add(add_material)
                db.session.commit()
                return redirect(f'/{process}/add_materials')
            except:
                return "При добавление произошла ошибка"
    return render_template('config_folder/add_materials.html', materials=materials, process=process, branch_footer=branch_footer, process_footer=process_footer)


# добавление оборудования
@app_routes.route('/<string:process>/add_equipment', methods=["POST", "GET"])
def add_equipment(process):
    from main import db
    from models import Equipment, Process

    branch_footer = db.session.query(Process).group_by(Process.branch).all()
    process_footer = db.session.query(Process).all()

    equipments = db.session.query(Process, Equipment).select_from(Equipment).join(Process).filter(Process.process == process).all()
  
    if request.method == "POST":
        equipment = request.form['equipment']
        process_id = db.session.query(Process.id).filter_by(process=process).all()[0][0]
    
        check_equipment = db.session.query(Equipment).filter_by(main=del_space_string(equipment)).first()
        if check_equipment is None:
            add_equipment = Equipment(process_id=process_id, main=del_space_string(equipment))
            try:
                db.session.add(add_equipment)
                db.session.commit()
                return redirect(f'/{process}/add_equipment')
            except:
                return "При добавление произошла ошибка"
                
    return render_template('config_folder/add_equipment.html', equipments=equipments, process=process, branch_footer=branch_footer, process_footer=process_footer)


# добавление оснастки
@app_routes.route('/<string:process>/add_tool', methods=["POST", "GET"])
def add_tool(process):
    from main import db
    from models import Equipment, Tool, Process

    
    equipments = db.session.query(Equipment, Process).select_from(Equipment).join(Process).filter(Process.process == process).all()

    branch_footer = db.session.query(Process).group_by(Process.branch).all()
    process_footer = db.session.query(Process).all()
   
    tools = db.session.query(Tool, Process, Equipment).select_from(Tool).join(Equipment).join(Process).filter(Process.process == process).all()
   
    if request.method == "POST":
        equipment_name = request.form['equipment']
        tool = request.form['tool']
        equipment_id = db.session.query(Equipment.id).filter_by(main=equipment_name).all()[0][0]
        
        check_tool = db.session.query(Tool).filter_by(tool=del_space_string(tool)).first()
        if check_tool is None:
            add_tool = Tool(tool=del_space_string(tool), equipment_id=equipment_id)
            try:
                db.session.add(add_tool)
                db.session.commit()
                return redirect(f'/{process}/add_tool')
            except:
                return "При добавление произошла ошибка"
                
    return render_template('config_folder/add_tool.html', equipments=equipments, tools=tools, process=process, branch_footer=branch_footer, process_footer=process_footer)


# добавление UPH
@app_routes.route('/<string:process>/add_uph', methods=["POST", "GET"])
def uph(process):
    from main import db
    from models import Process, Tpp_config
    
    branch_footer = db.session.query(Process).group_by(Process.branch).all()
    process_footer = db.session.query(Process).all()
    tpp_config = db.session.query(Tpp_config).filter_by(del_status=True).all()
        

    return render_template('config_folder/add_uph.html', process=process, tpp_config=tpp_config, branch_footer=branch_footer, process_footer=process_footer)


@app_routes.route('/<string:process>/update_uph/<int:id>', methods=["POST", "GET"])
def update_uph(process, id):
    from main import db
    from models import Process, Tpp_config, Uph

    form = UpdateUph()

    branch_footer = db.session.query(Process).group_by(Process.branch).all()
    process_footer = db.session.query(Process).all()
    tpp_config = db.session.query(Tpp_config).filter_by(del_status=True).all()
    print(process, id)
    data_uph = db.session.query(Uph).filter_by(id=id).all()
    uph_to_update = db.session.query(Uph).get_or_404(id)
    if request.method == "POST":
        uph_to_update.plan_uph = request.form["uph"]
        uph_to_update.process_id = db.session.query(Process.id).filter_by(process=process).all()
        uph_to_update.tpp_id = id
        try:
            db.session.commit()
            return redirect('/add_uph')
        except:
            return "При обновлении произошла ошибка"
 
    return render_template('config_folder/update_uph.html', form=form, data_uph=data_uph, process=process, tpp_config=tpp_config, branch_footer=branch_footer, process_footer=process_footer)