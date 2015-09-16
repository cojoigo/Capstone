(() ->
    app = angular.module('nosferatuApp', ['mm.foundation'])
    app.config(['$interpolateProvider', ($interpolateProvider) ->
        $interpolateProvider.startSymbol('{[')
        $interpolateProvider.endSymbol(']}')
    ])
    app.controller(
        'nosferatuController',
        ['$scope', '$log', '$http', '$timeout', ($scope, $log, $http, $timeout) ->
            submitButtonTexts = {false: 'Search for Node', true: 'Loading...'}
            $scope.loading = false
            $scope.submitButtonText = submitButtonTexts[$scope.loading]
            $scope.nodes = []

            $http.get('/registered_nodes')
                .success((results) ->
                    $log.log('registered nodes', results)
                    Array::push.apply($scope.nodes, results.items)
                    console.log('nodes!', $scope.nodes)
                )
                .error((error) ->
                    $log.log('Initial node list:', error)
                )

            $scope.searchForNode = () ->
                $log.log('Testing')

                $http.post('/register_node')
                    .success((results) ->
                        $log.log(results)
                        $scope.findNewNodes(results)
                        $scope.loading = true
                        $scope.submitButtonText = submitButtonTexts[$scope.loading]
                    )
                    .error((error) ->
                        $log.log(error)
                    )

            $scope.findNewNodes = (jobId) ->
                timeout = ''
                poller = () ->
                    $log.log('/registered_nodes/' + jobId)
                    $http.get('/registered_nodes/' + jobId)
                        .success((data, status, headers, config) ->
                            if status == 202
                                $log.log(data, status)
                            else if status == 200
                                $log.log(data)
                                $scope.loading = false
                                $scope.submitButtonText = submitButtonTexts[$scope.loading]
                                $scope.nodes.push(data)
                                console.log('data', data, $scope.nodes)
                                $timeout.cancel(timeout)
                                return false

                            # Continue to call the poller every 2 seconds until its canceled
                            timeout = $timeout(poller, 2000)
                        )
                poller()
        ])
)()
