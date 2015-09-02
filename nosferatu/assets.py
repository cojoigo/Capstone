from flask.ext.assets import Bundle, Environment
import webassets_ng_annotate


webassets_ng_annotate.register()
environment = Environment()
environment.register(
    'common_css',
    Bundle(
        'vendor/foundation/css/normalize.css',
        'vendor/foundation/css/foundation.min.css',
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
        'vendor/jquery/jquery-2.1.4.min.js',
        'vendor/foundation/js/foundation.min.js',
        'vendor/angular/angular.min.js',
        Bundle(
            'js/main.coffee',
            filters='coffeescript',
        ),
        filters='jsmin',
        output='public/js/common.js',
    )
)
