from flask import Flask, render_template
import pymysql

app = Flask(__name__)


@app.route('/')
@app.route('/index')
def index():
    return render_template(
        'index.html',
        title='Flask Template Test',
        home_str='Hello Flask!',
        home_list=[1, 2, 3, 4, 5]
    )


'''@app.route('/info')
def info():
    return render_template('info.html')'''

@app.route('/info')
def refinedata_api():
    conn = pymysql.connect(
        charset='utf8',
        db='dangamdb',
        host='ai.goormirang.io',
        password='dangam',
        port=3306,
        user='jjl'
    )
    curs = conn.cursor()
    sql = """SELECT convention_name, COUNT(convention_name) FROM refine_schedule GROUP BY convention_name"""
    curs.execute(sql)
    data_count = curs.fetchall()

    return render_template(
        'info.html',
        count=data_count
    )


if __name__ == '__main__':
    app.run()