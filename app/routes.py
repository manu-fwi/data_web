from flask import render_template,flash,url_for,redirect, request
from flask_sqlalchemy import inspect
from app import app
from app import models
from app import forms
from app import log
from app import graphs

@app.route('/')
@app.route('/index')
def index():
    messages = models.db_updates.query.all()
    return render_template('index.html', title='Home')

#get all dashboards db records
def get_dashboards():
    #messages = models.db_dashbord.query.all()
    #FIXME should send all dashboard db records
    dashboards=[]
    for i in range(10):
        dash ="dash numero "+str(i)
        dashboards.append(dash)
    return dashboards

#get all data_streams_head db records
def get_data_streams_head():
    return models.db_data_streams_head.query.all()

#get all data_streams_head db records
def get_graphs():
    inspector = inspect(models.db.engine)
    if inspector.has_table("graphs"):
        return models.db_graph.query.all()
    else:
        return []

@app.route('/create_dashboard',methods=['GET', 'POST'])
def create_dashboard():
    form=forms.DashboardCreateForm()
    if form.validate_on_submit():
        #Fixme check if this dashboard name is already taken
        log("dashboard create:"+form.name.data)
        return redirect('/index')
    return render_template('create_dashboard.html', title='Create Dashboard',form=form)

@app.route('/create_graph',methods=['GET', 'POST'])
def create_graph():
    form=forms.GraphCreateForm()
    if form.validate_on_submit():
        print(request.args)
        
        data_str_head = get_data_streams_head()[int(request.values.get('data_str_head'))-1]
        graphs.add_new_graph(request.form.get('name'),
                             int(request.form.get('graph'))-1,
                             "{}")
    return render_template('create_graph.html',
                           get_data_streams_head=get_data_streams_head,
                           title='Create graph',form=form)

@app.route('/view_dashboards')
def view_dashboards():

    return render_template('view_dashboards.html', title='View Dashboards', action="dashboard_view",
                           get_dashboards=get_dashboards)

@app.route('/view_graphs')
def view_graphs():

    return render_template('view_graphs.html', title='View graphs',
                           get_graphs=get_graphs)

@app.route('/dashboard_view/<string:dashboard_name>')
def dashboard_view(dashboard_name):
    return render_template('dashboard_view.html', title='View Dashboards',
                           dashboard_name=dashboard_name)

@app.route('/edit_graphs',methods=['GET', 'POST'])
def edit_graphs():
    form=forms.GraphEditForm()
    if form.validate_on_submit():
        #Fixme
        log("graph edit:"+form.name.data)
        print(request.form)
        return redirect('/index')

    return render_template('edit_graphs.html', title='Edit graphs', action="edit_graphs",
                           get_data_streams_head=get_data_streams_head,
                           get_graphs=get_graphs,
                           form=form)

@app.route('/dashboard_edit/<string:dashboard_name>',methods=['GET', 'POST'])
def dashboard_edit(dashboard_name):
    form=forms.DashboardEditForm(name=dashboard_name)

    if form.validate_on_submit():
        print(dashboard_name)
        return redirect('/view_dashboards')
    return render_template('dashboard_edit.html',
                           title='Edit Dashboard : '+dashboard_name,
                           get_dashboards=get_dashboards,
                           get_data_streams_head=get_data_streams_head,
                           form=form)


