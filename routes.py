from flask import render_template, request, redirect, Blueprint


app_routes = Blueprint("app_routes", __name__)


# Основная страница
@app_routes.route('/', methods=["POST", "GET"])
def index_page():
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

        resume = db.engine.execute(f"SELECT * FROM tpp WHERE prod_name='{prod_name}' AND tpp_stage='{tpp_stage}' AND process='{process}'").all()
  
        sum_qty = db.engine.execute(f"SELECT SUM(qty_in), SUM(qty_out) FROM tpp WHERE prod_name='{prod_name}' AND tpp_stage='{tpp_stage}' AND process='{process}'").all()[0]

        product = prod_name

    return render_template('index.html', resume=resume, sum_qty=sum_qty, process_list=process_list, product=product, product_list=product_list)


# Страница для входа
@app_routes.route('/login')
def login_page():
    return render_template('login.html')


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
        prod_name = request.form['master_add_product']
        tpp_stage = request.form['master_add_tpp_stage']
        comment = request.form['master_comment']

        config_product = Tpp_config(
            prod_name=prod_name,
            tpp_stage=tpp_stage,
            comment=comment
        )

        try:
            db.session.add(config_product)
            db.session.commit()
            return redirect('/config_page')
        except:
            return "При добавление произошла ошибка"

    else:
        return render_template('config_page.html', tpp_config=tpp_config)


# Страница для 404 ошибки
@app_routes.errorhandler(404)
def page_not_found(error):
    return render_template('page404.html')
