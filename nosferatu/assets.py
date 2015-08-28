from flask.ext.assets import Bundle, Environment

environment = Environment()
environment.register(
    'common_css', 
    Bundle(
        'vendor/foundation/css/foundation.min.css',
        Bundle(
            'css/layout.scss',
            filters='scss',
        ),
        filters='cssmin', output='public/css/common.css',
    ),
)
environment.register(
    'common_js',
    Bundle(
        'vendor/jquery/jquery-2.1.4.min.js',
        'vendor/foundation/js/foundation.min.js',
        Bundle(
            'js/main.coffee',
            filters='coffeescript',
        ),
        filters='jsmin', output='public/js/common.js',
    )
)
