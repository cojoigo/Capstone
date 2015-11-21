errFunc = () ->
    ((error) ->
        $log.log(error)
    )

pollFunc = (httpSomething, func, timeout, log) ->
    time = ''
    count = 0
    poller = () ->
        log.log("PollFuncing", count)
        httpSomething.then(
            ((results) ->
                if results.status in [202, 502]
                    log.log("  - failed:", results.data)
                    count += 1
                    if count is 3
                        timeout.cancel(time)
                        return false
                else if results.status == 200
                    func(results.data)
                    timeout.cancel(time)
                    return false

                # Continue to call the poller every 2 seconds until its canceled
                time = timeout(poller, 2000)
            ), errFunc
        )
    poller()

angular.module('nosferatuApp', [
    'mm.foundation',
])
.config(['$interpolateProvider', ($interpolateProvider) ->
    $interpolateProvider.startSymbol('{[')
    $interpolateProvider.endSymbol(']}')
])
