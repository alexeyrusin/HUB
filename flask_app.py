from flask import Flask, session, render_template, request, redirect, g, url_for, send_from_directory, make_response
import sqlite3
import os
from flask import jsonify
from werkzeug.utils import secure_filename
from werkzeug.contrib.fixers import ProxyFix
UPLOAD_FOLDER = 'download'

app = Flask(__name__)
app.url_map.strict_slashes = False
app.secret_key = os.urandom(24)


class get():
    qery = {
            'users':'SELECT * FROM users',
            '0archive':'SELECT * FROM tasks WHERE status=3',
            'list_executor':'SELECT * FROM executor_main ORDER BY type', 
			
            'create_tasks':'',
            'create_task_lines':'',
            'tasks_category':'SELECT * FROM tasks_category',
            'task_names':'SELECT * FROM task_names',
            'edit_tasks':'',
	    'user_control_task':'SELECT * FROM users',
            
            'add_tasks':'',
            
            'main':'SELECT * FROM data',
            'add':'',
            }

class post():
    qery = {
            'delete':'DELETE FROM data WHERE id=',
            'status0':'UPDATE data SET status=0 WHERE id=',
            'status1':'UPDATE data SET status=1 WHERE id=',
            }

def database_chat(db_qery):
    try:
        conn = sqlite3.connect('static/chat.db')
        c = conn.cursor()
        c.execute(db_qery)
        data = c.fetchall()
        conn.commit()
        return data
    except Exception as error:
        return str(error)
    
def database(db_qery):
    try:
        conn = sqlite3.connect('db.db')
        c = conn.cursor()
        c.execute(db_qery)
        data = c.fetchall()
        conn.commit()
        return data
    except Exception as error:
        return str(error)

def select_now():
    data = database('SELECT datetime("now", "+3 hours")')
    return data

def qery(data, what):
    time = select_now()
    one, two = '', ''
    for key, value in data.items():
        value2 = ""
        for v in value:
            if v == '"' or v == "'":
                value2+="|"
            else:
                value2+=str(v)
        one+= ',' + '"' + str(key)+ '"'
        two+= ',' + '"' + str(value2)+ '"'
    qery = "INSERT INTO "+str(what)+" ("+str(one[1:])+") VALUES ("+str(two[1:])+")"
    return qery

def update_qery(data):
    update_data = ''
    for key, value in data.items():
        update_data+= ',' + '' + str(key)+ '=' + '"' + str(value)+ '"'
    qery = 'UPDATE data SET '+str(update_data[1:])+' WHERE id='
    return qery

@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        if request.method == 'POST':
            data = database(get.qery['users'])
            for x in data:
                if x[2] == request.form['password'] and str(x[1]) == request.form['login']:
                    session['user_id'] = x[0]
                    session['user_rank'] = x[3]
                    session['user_rank_name'] = x[4]
                    session['user_name'] = x[5]
                    return redirect(url_for('main', value='main'))
        if 'user_id' in session:
            return redirect(url_for('main', value='main'))
        return render_template('login.html')
    except Exception as e :
        return str(e)

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = session['user_id']


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))
                 
@app.route('/download/<value1>/<value>', methods=['GET', 'POST'])
def static2(value1,value):
    if 'user_id' not in session:
        return str('нет доступа')
    directory = 'download/' + str(value1)
    return send_from_directory(directory, value)


#установка статуса исполнен для задачи
@app.route('/status_main/<value1>/<value2>', methods=['GET', 'POST'])
def status_main(value1, value2):
    if request.method == 'GET':
        db_qery = 'UPDATE tasks SET status='+str(value2)+' WHERE id IN (SELECT subtask.task_id FROM subtask WHERE subtask.id='+str(value1)+')'
        data = database(db_qery)       

@app.route('/0actual', methods=['GET', 'POST'])
def actual():
    if request.method == 'GET':
        data = database('SELECT * FROM tasks WHERE status!=3')
        return render_template('0actual.html', data=data)
    
@app.route('/boss/<value>', methods=['GET', 'POST'])
def boss(value):
    if request.method == 'GET':
        a = 'SELECT *, max(time_posted) FROM files_subtask INNER JOIN subtask ON subtask.id=files_subtask.subtask_id WHERE task_id='+str(value)+' AND name=6'
        files = database(a)
        return render_template('u_boss.html', files=files)
        
    
#добавление заданий
@app.route('/create_task_lines/<value>', methods=['GET', 'POST'])
def create_task_lines(value):
    if request.method == 'GET':
        db_qery ='SELECT * FROM task_lines WHERE task_id='+ str(value)
        data = database(db_qery)
        return render_template('create_task_lines.html', data=data, value=value)
    data = request.form.to_dict()
    db_qery = qery(data, 'task_lines')
    final = database(str(db_qery))

@app.route('/to_archive/<value>', methods=['GET', 'POST'])
def to_archive(value):
    if request.method == 'GET':
        db_qery ='UPDATE tasks SET status=3 WHERE id=' + str(value)
        data = database(db_qery)
        return str(db_qery)
    
@app.route('/from_archive/<value>', methods=['GET', 'POST'])
def from_archive(value):
    if request.method == 'GET':
        db_qery ='UPDATE tasks SET status=2 WHERE id=' + str(value)
        data = database(db_qery)
        return str(db_qery)

#Смена статуса
@app.route('/status/<value1>/<value2>', methods=['GET', 'POST'])
def status(value1, value2):
    if request.method == 'GET':
        db_qery ='UPDATE subtask SET status='+str(value2)+' WHERE id=' + str(value1)
        data = database(db_qery)
        return str(db_qery)

#Показывает исполнителей задачи
@app.route('/executors/<value>', methods=['GET', 'POST'])
def executors(value):
    if request.method == 'GET':
        db_qery = 'SELECT * FROM users WHERE users.id IN (SELECT user_id FROM executor_subtask WHERE executor_subtask.subtask_id='+str(value)+')'
        data = database(db_qery)
        return render_template('executors.html', data=data)

@app.route('/isp', methods=['GET', 'POST'])
def isp():
    if request.method == 'GET':
        a = 'SELECT * FROM tasks, subtask WHERE subtask.id IN (SELECT subtask_id FROM executor_subtask WHERE user_id='+str(session['user_id'])+') AND subtask.task_id = tasks.id AND tasks.status!=3 AND tasks.status!=4'
        data = database(a)

        b = 'SELECT * FROM comment_subtask WHERE subtask_id IN (SELECT subtask_id FROM executor_subtask WHERE user_id='+str(session['user_id'])+')'
        comment = database(b)
        
        c = 'SELECT * FROM files_subtask WHERE subtask_id IN (SELECT subtask_id FROM executor_subtask WHERE user_id='+str(session['user_id'])+')'
        #c = 'SELECT * FROM files_subtask INNER JOIN tasks ON tasks.id=files_subtask.user_id WHERE subtask_id IN (SELECT subtask_id FROM executor_subtask WHERE user_id='+str(session['user_id'])+')'
        files = database(c)

        tasks_category = database(get.qery['tasks_category'])
        return render_template('isp.html', data=data, files=files, comment=comment, tasks_category=tasks_category)

@app.route('/ob/<value>', methods=['GET', 'POST'])
def ob(value):
    if request.method == 'GET':
        a = 'SELECT *, max(time_posted) FROM files_subtask INNER JOIN subtask ON subtask.id=files_subtask.subtask_id  WHERE subtask_id IN (SELECT id FROM subtask WHERE task_id='+str(value)+') GROUP BY subtask_id'
        #a = 'SELECT *, max(time_posted) FROM files_subtask INNER JOIN tasks ON tasks.id=files_subtask.user_id  WHERE subtask_id IN (SELECT id FROM subtask WHERE task_id='+str(value)+') GROUP BY subtask_id'
        files = database(a)

##        def executors(value):
##            db_qery = 'SELECT * FROM users WHERE users.id IN (SELECT user_id FROM executor_subtask WHERE executor_subtask.subtask_id='+str(value)+')'
##            data = database(db_qery)
##            return data
##        return render_template('u_all.html', files=files, data=executors(value))
        return render_template('u_all.html', files=files)
        

@app.route('/upload/<value>', methods=['GET', 'POST'])
def upload_file(value):
    if request.method == 'POST':
        uploaded_files = request.files.getlist("file[]")
        upload_dir = 'download/' + str(value)
        files = os.listdir('download/' + str(value))
        new = 0
        for f in files:
            new+=1
        for file in uploaded_files:
            name = file.filename.split('.')[-1]
            sec_name = str(new)+'.'+str(name)
            file.save(os.path.join(upload_dir, sec_name))
            time = select_now()[0]
            qery = "INSERT INTO files_subtask (subtask_id, file_name, time_posted, user_id) VALUES (" + "'" + str(value)+ "','" + str(sec_name) + "','" + str(time[0]) + "','" + str(session['user_id']) + "')"
            final = database(qery)
            status =  database("UPDATE subtask SET status=3 WHERE id="+str(value))
            return redirect('main')
    #GET
    files = database('SELECT * FROM files_subtask WHERE subtask_id='+str(value)+' ORDER BY time_posted DESC LIMIT 1')
    return render_template('u.html', files=files)

#Чат
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'GET':
        db_qery ='SELECT * FROM chat ORDER BY time_posted DESC'
        data = database_chat(db_qery)
        return render_template('chat.html', data=data)
    time = select_now()[0]
    one = request.form['one']
    db_qery = "INSERT INTO chat (user_name, time_posted, text) VALUES ('" + str(session['user_name']) + "' , '" +  str(time[0]) + "' , '" + str(one) + "')"
    final = database_chat(str(db_qery))

#редактор заданий
@app.route('/edit_task_lines/<value>', methods=['GET', 'POST'])
def edit_task_lines(value):
    if request.method == 'GET':
        db_qery ='SELECT * FROM task_lines WHERE task_id='+ str(value)
        data = database(db_qery)

        users = database(get.qery['user_control_task'])
        task_names = database(get.qery['task_names'])
        return render_template('edit_task_lines.html', data=data, value=value, users=users, task_names=task_names)

#Добавление экспертов
@app.route('/add_executor/<value>', methods=['GET', 'POST'])
def add_executor(value):
    if request.method == 'GET':
        db_qery ='SELECT * FROM task_lines WHERE task_id='+ str(value)
        data = database(db_qery)

        users = database(get.qery['user_control_task'])
        task_names = database(get.qery['task_names'])
        return render_template('edit_task_lines.html', data=data, value=value, users=users, task_names=task_names)
  
@app.route('/<value>', methods=['GET', 'POST'])
def main(value):
    if g.user:
        try:
            if request.method == 'GET':
                cur_date = select_now()
                for x in get.qery:
                    if value==x:
                        data = database(get.qery[x])
                        url = str(x)+'.html'
                        if value=='users':
                            users = database(get.qery['users'])
                            executor = database(get.qery['list_executor'])
                            return render_template(url, users=users, executor=executor)
                        else:
                            return render_template(url, value=value, data=data, cur_date=cur_date[0])
    ##POST
            else:
                for x in post.qery:
                    if value==x:
                        __init__ = request.form[str(x)]
                        db_qery = post.qery[x] + str(__init__)
                        data = database(str(db_qery))
                        return redirect(url_for('main', value='main'))
                    else:
                        pass
						
                if value=='users':
                    data = request.form.to_dict()
                    db_qery = qery(data, 'users')
                    final = database(str(db_qery))
                    return redirect(url_for('main', value='main'))

                #Добавление экспертов к задаче
                if value=='create_new_tasks':
                    data = request.form.to_dict()
                    db_qery = qery(data, 'tasks')
                    final = database(str(db_qery))

                    db_qery2 = "SELECT MAX(id) FROM tasks"
                    task_maxid = database(str(db_qery2))
                    task_maxid = task_maxid[0]
                    add_executor = 'add_executor/' + str(task_maxid[0])

                    executor = database(get.qery['list_executor'])
                    
                    #Создает subtask с использованием основной матрици
                    for x in range(1, 7):
                        db_qery3 = "INSERT INTO subtask (task_id, name) VALUES ('" + str(task_maxid[0]) + "' , '" + str(x) + "')"
                        final = database(str(db_qery3))
                        

                        #select subtask
                        db_qery4 = "SELECT MAX(id) FROM subtask"
                        maxid = database(str(db_qery4))
                        maxid = maxid[0]
                        
                        for e in executor:
                            if str(e[0]) == str(x):
                                upload_dir = 'download/' + str(str(maxid[0]))
                                os.mkdir(str(upload_dir))
                                db_qery5 = "INSERT INTO executor_subtask (subtask_id, user_id) VALUES ('" + str(maxid[0]) + "' , '" + str(e[1]) + "')"
                                final = database(str(db_qery5))
                            else:
                                pass
                    return redirect(url_for('main', value='main'))


                
                #добавление значения в перечень tasks_category
                if value=='add_tasks_category':
                    one = request.form['one']
                    db_qery = "INSERT INTO tasks_category (name) VALUES ('" + str(one) + "')"
                    final = database(str(db_qery))
                #удаление значения в перечень tasks_category
                if value=='remove_tasks_category':
                    one = request.form['one']
                    db_qery = "DELETE FROM tasks_category WHERE id='"+ str(one)  + "'"
                    final = database(str(db_qery))


##ЗАДАНИЯ
                    
                #добавление значения в перечень task_names
                if value=='add_task_names':
                    one = request.form['one']
                    db_qery = "INSERT INTO task_names (name) VALUES ('" + str(one) + "')"
                    final = database(str(db_qery))
                #удаление значения в перечень task_names
                if value=='remove_task_names':
                    one = request.form['one']
                    db_qery = "DELETE FROM task_names WHERE id='"+ str(one) + "'"
                    final = database(str(db_qery))
                if value=='remove_task_lines':
                    two = request.form['two']
                    db_qery = "DELETE FROM task_lines WHERE id='"+ str(two) + "'"
                    final = database(str(db_qery))
                
                                      
        except Exception as e :
            return str(e)

@app.route('/sitemap.xml')
def sitemap():
    try:
        sitemap_xml = render_template('sitemap.xml')
        response= make_response(sitemap_xml)
        response.headers["Content-Type"] = "application/xml"
        return response
    except Exception as e:
        return(str(e))

if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD']=True
    app.run(debug=True,use_reloader=True,   host="192.168.0.108", port=5000)
