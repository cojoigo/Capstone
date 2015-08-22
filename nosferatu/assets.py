from flask.ext.assets import Bundle, Environment
from nosferatu import app

environment = Environment(app)
common_css = Bundle(
    'vendor/foundation/css/foundation.min.css',
    Bundle(
        'css/layout.scss',
        filters='scss',
    ),
    filters='cssmin', output='public/css/common.css',
)
common_js = Bundle(
    'vendor/jquery/jquery-2.1.4.min.js',
    'vendor/foundation/js/foundation.min.js',
    Bundle(
        'js/main.coffee',
        filters='coffeescript',
    ),
    filters='jsmin', output='public/js/common.js',
)
environment.register('common_css', common_css)
environment.register('common_js', common_js)
