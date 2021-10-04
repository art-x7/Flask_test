from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tpp.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

with app.app_context():
    from sql import Tpp

    db.create_all()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/form', methods=["POST", "GET"])
def form():
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
        return render_template('process/form.html')


"""REPORT"""


@app.route('/report')
def report():
    tpps = db.session.query(Tpp).all()
    product = ["GS1", "NAND", "Micron", "1890"]
    return render_template('report.html', tpps=tpps, product=product)


@app.route('/report/<string:product>')
def report_f(product):
    product_s = product
    tpp = ["ТПП единичных изделий", "ТПП серийных изделий"]
    return render_template('report_f.html', tpp=tpp, product_s=product_s)


@app.route('/report/<string:product>/<string:tpp>/')
def list(product, tpp):
    product_p = product
    tpp_p = tpp
    resume = db.session.query(Tpp).all()
    uniq_process = {i[0] for i in db.session.query(Tpp.process).all()}
    return render_template('list_tpp.html', resume=resume, tpp_p=tpp_p, product_p=product_p, uniq_process=uniq_process)


@app.route('/tpp_report/<string:product>/<string:tpp>/<string:uniq_process>/')
def process_report(product, tpp, uniq_process):
    resume = Tpp.query.filter(Tpp.process == uniq_process).all()
    sum_qty = db.engine.execute(f"SELECT SUM(qty_in), SUM(qty_out) FROM tpp WHERE tpp.process='{uniq_process}'")
    print(sum_qty.all())

    return render_template('process_report.html', resume=resume, tpp=tpp, product=product, uniq_process=uniq_process, )


@app.route('/master', methods=["POST", "GET"])
def master():
    data = {
        "GS1": ["ТПП единичных изделий", 1],
        "NAND": ["ТПП единичных изделий", 2],
        "Micron": ["ТПП серийных изделий", 1],
        "1890": ["ТПП серийных изделий", 2],
    }

    len_data = len(data)
    return render_template('master.html', data=data, len_data=len_data)


@app.errorhandler(404)
def pageNotFound(error):
    return render_template('page404.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=False)
