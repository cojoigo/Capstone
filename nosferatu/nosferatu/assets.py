from flask.ext.assets import Bundle, Environment


environment = Environment()
environment.register(
    'common_css',
    Bundle(
        'css/lib/foundation.min.css',
        'css/lib/normalize.min.css',
        Bundle(
            'css/base.scss',
            filters='scss',
        ),
        filters='cssmin', output='public/css/common.css',
    ),
)
environment.register(
    'common_js',
    Bundle(
        'js/lib/jquery.min.js',
        'js/lib/angular.min.js',
        'js/lib/foundation.min.js',
        'js/lib/mm-foundation-tpls-0.6.0.min.js',
        Bundle(
            'js/app.coffee',
            filters='coffeescript',
        ),
        filters='jsmin',
        output='public/js/common.js',
    )
)
