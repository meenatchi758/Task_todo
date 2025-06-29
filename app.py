from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///task_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# =======================
# Models
# =======================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='To Do')
    priority = db.Column(db.String(10))
    progress = db.Column(db.Integer, default=0)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Ensure progress is always between 0 and 100
    def set_progress(self, value):
        try:
            val = int(value)
            if val < 0:
                self.progress = 0
            elif val > 100:
                self.progress = 100
            else:
                self.progress = val
        except (ValueError, TypeError):
            self.progress = 0

# =======================
# Routes
# =======================

@app.route('/')
def index():
    projects = Project.query.all()
    tasks = Task.query.order_by(Task.due_date).all()
    # Debug print to check progress values
    for t in tasks:
        print(f"Task: {t.title}, Progress: {t.progress} (type: {type(t.progress)})")
    return render_template('index.html', projects=projects, tasks=tasks)

@app.route('/project/create', methods=['POST'])
def create_project():
    name = request.form['name']
    if name:
        project = Project(name=name)
        db.session.add(project)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/task/create', methods=['POST'])
def create_task():
    title = request.form['title']
    description = request.form['description']
    due_date_str = request.form['due_date']
    priority = request.form['priority']
    project_id = request.form['project_id']
    assigned_to = request.form['assigned_to']

    try:
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
    except ValueError:
        due_date = datetime.today()

    task = Task(
        title=title,
        description=description,
        due_date=due_date,
        priority=priority,
        project_id=project_id,
        assigned_to=assigned_to
    )
    # Set progress explicitly to 0 on creation
    task.set_progress(0)

    db.session.add(task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/task/update/<int:id>', methods=['POST'])
def update_task(id):
    task = Task.query.get_or_404(id)
    task.status = request.form['status']

    task.set_progress(request.form.get('progress', 0))

    db.session.commit()
    return redirect(url_for('index'))

@app.route('/kanban')
def kanban():
    tasks = Task.query.all()
    return render_template('kanban.html', tasks=tasks)

@app.route('/calendar')
def calendar():
    tasks = Task.query.all()
    return render_template('calendar.html', tasks=tasks)

# =======================
# Init + Run
# =======================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
