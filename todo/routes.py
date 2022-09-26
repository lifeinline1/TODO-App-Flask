import sqlite3
from todo import app
from flask import render_template, redirect, url_for, flash, request
from todo.models import Task, User
from todo.forms import AddTask, RegisterForm, LoginForm, AddTask, TaskDone, TaskEdit, TaskDelete
from todo import db
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime


@app.route('/')
@app.route('/home')
def hello():
    return render_template('home.html')

@app.route('/todo', methods=['GET','POST'])
@login_required
def todo_page():
    
    task_done_form = TaskDone()
    task_edit_form = TaskEdit()
    task_delete_form = TaskDelete()
    form = AddTask()
    date = datetime.now()

    if task_done_form.validate_on_submit():
        print(task_done_form)

    if request.method == "POST":
        task_to_add = Task(name=form.task.data,
                            entry=date.strftime("%d/%m/%y"),
                            owner=current_user.id)
        
        db.session.add(task_to_add)
        db.session.commit()

        return redirect(url_for('todo_page'))
        
        
    items = Task.query.filter_by(owner=current_user.id)

    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error: {err_msg}', category='danger')
    
    if request.method == "GET":
        items = Task.query.filter_by(owner=current_user.id)
        return render_template('todo.html', items=items, 
                                            form=form,
                                            task_done_form=task_done_form,
                                            task_edit_form=task_edit_form,
                                            task_delete_form=task_delete_form)

@app.route('/register', methods=['GET','POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                            email_address=form.email_address.data,
                            password=form.password1.data)

        db.session.add(user_to_create)
        db.session.commit()
        
        return redirect(url_for('todo_page'))

    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error: {err_msg}', category='danger')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET','POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
            attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Logged in as {attempted_user.username}', category='success')
            return redirect(url_for('todo_page'))
        else:
            flash('Username and password don\'t match', category='danger')


    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET','POST'])
def logout_page():
    logout_user()
    flash('You have been logged out!', category='info')
    return redirect(url_for('hello'))