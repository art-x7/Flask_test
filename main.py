import pdfkit

from flask import Flask, render_template, request, redirect, make_response
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tpp.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

with app.app_context():
    from create_db import *

    db.create_all()

#Основная страница
@app.route('/')
def index_page():
    return render_template('index.html')

#Страница для входа
@app.route('/login')
def login_page():
    return render_template('login.html')

#Страница для заполнения отчета
@app.route('/form', methods=["POST", "GET"])
def input_form_page():
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


#REPORT

#Страница для выбора продукта
@app.route('/tpp_report')
def tpp_report_choice_product():
    product = {i[0] for i in  db.engine.execute(f"SELECT prod_name FROM Tpp_config ORDER BY prod_name").all()}
   
    return render_template('choice_product.html', product=product)


#Страница для выбора стадии ТПП
@app.route('/tpp_report/<string:product>/')
def tpp_report_choice_types_tpp(product):
    tpp_config = {i[0] for i in  db.engine.execute(f"SELECT tpp_stage FROM Tpp_config WHERE prod_name='{product}' ORDER BY tpp_stage").all()}

    return render_template('choice_types_tpp.html', tpp_config=tpp_config, product=product)


#Страница для выбора процесса
@app.route('/tpp_report/<string:product>/<string:tpp>/')
def tpp_report_choice_process(product, tpp):
    uniq_process = {i[0] for i in  db.engine.execute(f"SELECT process FROM tpp WHERE prod_name='{product}' AND tpp_stage='{tpp}'").all()}
       
    return render_template('choice_process.html', tpp=tpp, product=product, uniq_process=uniq_process)


#Страница для вывода сводного отчета по процессу
@app.route('/tpp_report/<string:product>/<string:tpp>/<string:uniq_process>/')
def tpp_report_resume(product, tpp, uniq_process):
    resume = {i for i in  db.engine.execute(f"SELECT * FROM tpp WHERE process='{uniq_process}' ORDER BY id + 0 desc").all()}
    print(resume)
    sum_qty = db.engine.execute(f"SELECT SUM(qty_in), SUM(qty_out) FROM tpp WHERE tpp.process='{uniq_process}'").all()[0]

    #html = render_template('report_resume.html', resume=resume, tpp=tpp, product=product, uniq_process=uniq_process, sum_qty=sum_qty)
    
    #pdf = pdfkit.from_string(html, False)
    #response = make_response(pdf)
    #response.headers["Content-Type"] = "application/pdf"
    #response.headers["Content-Disposition"] = "inline; filename=output.pdf"

    #return response
    return render_template('report_resume.html', resume=resume, tpp=tpp, product=product, uniq_process=uniq_process, sum_qty=sum_qty)

#Страница для конфигурирования ТПП
@app.route('/config_page', methods=["POST", "GET"])
def config_page():
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


#Страница для 404 ошибки
@app.errorhandler(404)
def page_not_found(error):
    return render_template('page404.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=False)
