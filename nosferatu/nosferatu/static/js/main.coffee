(() ->
    app = angular.module('nosferatuApp', ['mm.foundation'])
    app.config(['$interpolateProvider', ($interpolateProvider) ->
        $interpolateProvider.startSymbol('{[')
        $interpolateProvider.endSymbol(']}')
    ])
    app.directive('ngFoundNode', () ->
        template = '
            <form role="form" ng-submit="addThisNode(nodeId)">
              <input type="text" name="nodeId" ng-model="nodeId" value="{[node.id]}" />
              <div class="row">
                <div class="small-4 columns">
                  <input type="text" placeholder="Node Name" />
                </div>
                <div class="small-4 columns">
                  <label>Node IP:
                    <label>{[node.ip]}</label>
                  </label>
                </div>
                <div class="small-4 columns">
                  <label>Node MAC:
                    <label>{[node.mac]}</label>
                  </label>
                </div>
              </div>
              <div class="row">
                <div class="small-4 columns"></div>
                <div class="small-4 columns">
                  <button type="button" ng-click="testFoundNode(nodeId)">{[testNodeBtnText]}</button>
                </div>
                <div class="small-4 columns">
                  <button type="submit" class="btn btn-default" ng-disabled="addingNode">Save</button>
                </div>
              </div>
            </form>
        '

        controller = ['$scope', '$log', '$http', ($scope, $log, $http) ->
            $log.log('Beginning of foundNode directive controller')

            $scope.testFoundNode = (nodeId) ->
                $log.log("Testing node #{nodeId}")
                action = 'start'
                if not $scope.testingNode
                    action = 'stop'
                $scope.testingNode = not $scope.testingNode

                $http.get("/nodes/#{nodeId}/test/#{action}")

            $scope.addThisNode = (nodeId) ->
                $log.log("Adding node #{nodeId}")
                if $scope.foundNodes.length == 0
                    $scope.findingNodes = false
        ]

        link = (scope, elem, attrs, ctrl) ->
            return

        return {
            bindToController: true,
            controller: controller
            controllerAs: 'vm'
            restrict: 'E'
            require: '^ngModel'
            scope: {
                ngModel: '='
            }
            template: template
            # link: link
        }
    ])
    app.controller(
        'nosferatuController',
        ['$scope', '$log', '$http', '$timeout', ($scope, $log, $http, $timeout) ->
            submitButtonTexts = {false: 'Search for Node', true: 'Loading...'}
            $scope.findingNodes = false
            $scope.submitButtonText = submitButtonTexts[$scope.findingNodes]

            $scope.testingNode = false
            testNodeBtnTexts = {false: 'Test', true: 'Stop'}
            $scope.testNodeBtnText = testNodeBtnTexts[$scope.testingNode]

            $scope.addingNode = false

            $scope.nodes = []
            $scope.foundNodes = []

            $scope.loadExistingNodes = (jobId) ->
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

            $scope.findNodes = () ->
                $log.log('Searching for new nodes')

                $http.post('/find_nodes')
                    .success((results) ->
                        $log.log("  ", results)
                        $scope.findNodesPoll(results)
                        $scope.findingNodes = true
                        $scope.submitButtonText = submitButtonTexts[$scope.findingNodes]
                    )
                    .error((error) ->
                        $log.log(error)
                    )

            $scope.findNodesPoll = (jobId) ->
                timeout = ''
                poller = () ->
                    $log.log('/find_nodes/' + jobId)
                    $http.get('/find_nodes/' + jobId)
                        .success((data, status, headers, config) ->
                            if status == 202
                                $log.log("  failed:", data, status)
                            else if status == 200
                                $log.log("  success: ", data)
                                Array::push.apply($scope.foundNodes, data.items)
                                console.log('    data', $scope.foundNodes)

                                if $scope.foundNodes.length == 0
                                    $scope.findingNodes = false
                                $scope.submitButtonText = submitButtonTexts[$scope.findingNodes]
                                $timeout.cancel(timeout)
                                return false

                            # Continue to call the poller every 2 seconds until its canceled
                            timeout = $timeout(poller, 2000)
                        )
                poller()
        ]
    )
)()
