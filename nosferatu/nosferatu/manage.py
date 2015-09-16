from flask_assets import ManageAssets
from assets import environment
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager

from nosferatu import app, db

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)
manager.add_command('assets', ManageAssets(environment))

if __name__ == '__main__':
    manager.run()
