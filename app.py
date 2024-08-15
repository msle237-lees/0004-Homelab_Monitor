import argparse
import os
import logging
from logging.handlers import SMTPHandler
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import datetime
import json

if __name__ == '__main__':
    args = argparse.ArgumentParser()

    args.add_argument('--ip', help='The IP address of the server', default='localhost', type=str)
    args.add_argument('-p', '--port', help='The port of the server', type=int)

    args = args.parse_args()

    with open('configs/config.json', 'r') as f:
        config = json.load(f)
    url = config['url']
    ntfy_subject = config['ntfy_subject']

    # create the flask app
    app = Flask(__name__)

    # create the database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    db = SQLAlchemy(app)

    # Set up error logging to send errors to the ntfy server
    class NtfyLoggingHandler(logging.Handler):
        def emit(self, record):
            try:
                ntfy_message = self.format(record)
                ntfy_server = f"{url}/{ntfy_subject}"
                os.system(f'ntfy -d "{ntfy_message}" {ntfy_server}')
            except Exception:
                self.handleError(record)

    ntfy_handler = NtfyLoggingHandler()
    ntfy_handler.setLevel(logging.ERROR)
    ntfy_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    app.logger.addHandler(ntfy_handler)

    # Create the database tables
    class Servers(db.Model):
        id = db.Column(db.Integer, primary_key=True, default=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        name = db.Column(db.String(100), nullable=False)
        cpu_type = db.Column(db.String(100), nullable=False)
        cpu_cores = db.Column(db.Integer, nullable=False)
        ram = db.Column(db.Integer, nullable=False)
        disk_space = db.Column(db.Integer, nullable=False)
        ip = db.Column(db.String(100), nullable=False)
        port = db.Column(db.Integer, nullable=False)
        status = db.Column(db.String(100), nullable=False)
        last_updated = db.Column(db.String(100), nullable=False)

        def __repr__(self):
            return '<Server %r>' % self
        
    class ServerStats(db.Model):
        id = db.Column(db.Integer, primary_key=True, default=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        server_id = db.Column(db.Integer, nullable=False, foreign_key=[Servers.id])
        cpu_usage = db.Column(db.Float, nullable=False)
        ram_usage = db.Column(db.Float, nullable=False)
        disk_total = db.Column(db.Float, nullable=False)
        disk_free = db.Column(db.Float, nullable=False)
        disk_usage = db.Column(db.Float, nullable=False)
        time = db.Column(db.String(100), nullable=False)

        def __repr__(self):
            return '<ServerStats %r>' % self
        
    # Create the database routes
    @app.route('/get_servers', methods=['GET'])
    def get_servers():
        servers = Servers.query.all()
        servers_list = []
        for server in servers:
            servers_list.append({
                'id': server.id,
                'name': server.name,
                'cpu_type': server.cpu_type,
                'cpu_cores': server.cpu_cores,
                'ram': server.ram,
                'disk_space': server.disk_space,
                'ip': server.ip,
                'port': server.port,
                'status': server.status,
                'last_updated': server.last_updated
            })
        return json.dumps(servers_list)

    @app.route('/get_server_stats', methods=['GET'])
    def get_server_stats():
        server_id = request.args.get('server_id')
        server_stats = ServerStats.query.filter_by(server_id=server_id).all()
        server_stats_list = []
        for stat in server_stats:
            server_stats_list.append({
                'id': stat.id,
                'server_id': stat.server_id,
                'cpu_usage': stat.cpu_usage,
                'ram_usage': stat.ram_usage,
                'disk_total': stat.disk_total,
                'disk_free': stat.disk_free,
                'disk_usage': stat.disk_usage,
                'time': stat.time
            })
        return json.dumps(server_stats_list)

    @app.route('/add_server', methods=['POST'])
    def add_server():
        name = request.form['name']
        cpu_type = request.form['cpu_type']
        cpu_cores = request.form['cpu_cores']
        ram = request.form['ram']
        disk_space = request.form['disk_space']
        ip = request.form['ip']
        port = request.form['port']
        status = request.form['status']
        last_updated = request.form['last_updated']
        new_server = Servers(name=name, cpu_type=cpu_type, cpu_cores=cpu_cores, ram=ram, disk_space=disk_space, ip=ip, port=port, status=status, last_updated=last_updated)
        db.session.add(new_server)
        db.session.commit()
        return redirect(url_for('get_servers'))

    @app.route('/add_server_stat', methods=['POST'])
    def add_server_stat():
        server_id = request.form['server_id']
        cpu_usage = request.form['cpu_usage']
        ram_usage = request.form['ram_usage']
        disk_total = request.form['disk_total']
        disk_free = request.form['disk_free']
        disk_usage = request.form['disk_usage']
        time = request.form['time']
        new_server_stat = ServerStats(server_id=server_id, cpu_usage=cpu_usage, ram_usage=ram_usage, disk_usage=disk_usage, time=time)
        db.session.add(new_server_stat)
        db.session.commit()
        return redirect(url_for('get_server_stats'))

    @app.route('/update_server', methods=['POST'])
    def update_server():
        server_id = request.form['server_id']
        server = Servers.query.get(server_id)
        server.name = request.form['name']
        server.cpu_type = request.form['cpu_type']
        server.cpu_cores = request.form['cpu_cores']
        server.ram = request.form['ram']
        server.disk_space = request.form['disk_space']
        server.ip = request.form['ip']
        server.port = request.form['port']
        server.status = request.form['status']
        server.last_updated = request.form['last_updated']
        db.session.commit()
        return redirect(url_for('get_servers'))

    @app.route('/delete_server', methods=['POST'])
    def delete_server():
        server_id = request.form['server_id']
        server = Servers.query.get(server_id)
        db.session.delete(server)
        db.session.commit()
        return redirect(url_for('get_servers'))
    
    @app.route('/delete_server_stat', methods=['POST'])
    def delete_server_stat():
        server_stat_id = request.form['server_stat_id']
        server_stat = ServerStats.query.get(server_stat_id)
        db.session.delete(server_stat)
        db.session.commit()
        return redirect(url_for('get_server_stats'))
    
    @app.route('/send_warning', methods=['POST'])
    def send_warning():
        ntfy_server = url + ntfy_subject
        server_id = request.form['server_id']
        server = Servers.query.get(server_id)
        os.system(f'ntfy -d "{server_id} WARNING - {server.name} - {server.ip} - {server.port} - {server.status} - {server.last_updated} - {server.cpu_type} - {server.cpu_cores} - {server.ram} - {server.disk_space}" {ntfy_server}')
        return 201
    
    @app.route('/')
    def index():
        return render_template('index.html')

    with app.app_context():
        db.create_all()
    app.run(debug=True, host=args.ip, port=args.port)
