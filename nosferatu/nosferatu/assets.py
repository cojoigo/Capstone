from flask.ext.assets import Bundle, Environment


environment = Environment()
environment.register(
    'common_css',
    Bundle(
        'vendor/foundation/css/foundation.min.css',
        'vendor/foundation/css/normalize.css',
        Bundle(
            'css/main.scss',
            filters='scss',
        ),
        filters='cssmin', output='public/css/common.css',
    ),
)
environment.register(
    'common_js',
    Bundle(
        # 'vendor/jquery/jquery-2.1.4.min.js',
        'vendor/angular/angular.min.js',
        # 'vendor/foundation/js/foundation.min.js',
        'vendor/foundation/js/mm-foundation-tpls-0.6.0.min.js',
        Bundle(
            'js/main.coffee',
            filters='coffeescript',
        ),
        filters='jsmin',
        output='public/js/common.js',
    )
)
