__author__ = 'Shinobu'
from fabric.api import *
from fabric.colors import green
import datetime

env.user = 'ubuntu'
env.host_string = '134.209.121.248'
env.password = 'peperonchino2'
home_path = "/home/ubuntu"
backups_path = "/home/ubuntu/Miprepa"
settings_production = "--settings='miprepa.settings.production'"
activate_env_production = "source {}/miprepaenv/bin/activate".format(home_path)
project_name = "Miprepa"
manage = "python manage.py"


def deploy_production():
    print("Beginning Deploy:")
    with cd("{}/Miprepa".format(home_path)):
        run("git pull origin master")
        run("{} && {} collectstatic --noinput {}".format(activate_env_production, manage,
                                                         settings_production))
        run("{} && {} migrate {}".format(activate_env_production, manage, settings_production))
        sudo("service nginx restart", pty=False)
        sudo("supervisorctl restart gunicorn_miprepa", pty=False)
    print(green("Deploy Miprepa successful"))


def createsuperuser_production():
    with cd("{}/Miprepa".format(home_path)):
        run("{} && {} createsuperuser {}".format(activate_env_production, manage,
                                                 settings_production))
    print(green("Createsuperuser successful"))


def backup():
    today = datetime.datetime.now()
    backup_name = "backup-{}-{}-{}.sql".format(today.day, today.month, today.year)
    print("Beginning Backup:")
    with cd(backups_path):
        sudo("pg_dump {}db -U postgres -h localhost > {}".format(project_name, backup_name))
        get(backup_name, backup_name)
    print("Backup downloaded.")
