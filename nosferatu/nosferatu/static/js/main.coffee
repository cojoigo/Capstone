(() ->
    app = angular.module('nosferatuApp', ['mm.foundation'])
    app.config(['$interpolateProvider', ($interpolateProvider) ->
        $interpolateProvider.startSymbol('{[')
        $interpolateProvider.endSymbol(']}')
    ])
    app.directive('foundNodeset', () ->
        template = '''
          <div role="tabpanel">
            <ul class="nav nav-tabs" role="tablist">
              <li role="presentation"
                  ng-repeat="node in nodeset.nodes">
                  ng-class="{'active': node.active}"
                <a href=""
                   role="tab"
                   ng-click="nodeset.select(node)">
                    {[node.heading]}
                </a>
              </li>
            </ul>
            <div ng-repeat="node in nodeset.nodes" ng-transclude></div>
          </div>
        '''
        controller = ['$scope', '$log', '$http', ($scope, $log, $http) ->
            $log.log('Beginning of foundNode directive controller')
            console.log('nodeset scope', this)

            this.nodes = []
            console.log('nodes', this.nodes)
            this.testingNode = false
            this.testNodeBtnTexts = {false: 'Test', true: 'Stop'}
            this.testNodeBtnText = this.testNodeBtnTexts[$scope.testingNode]

            this.testFoundNode = () ->
                nodeId = this.$id
                $log.log("Testing node #{nodeId}")
                action = 'start'
                if not this.testingNode
                    action = 'stop'
                this.testingNode = not this.testingNode

                $http.get("/nodes/#{nodeId}/test/#{action}")

            this.addNode = (node) ->
                this.log("Adding node #{node}")
                this.nodes.push(node)
                if this.tabs.length == 1
                    node.active = true

            this.select = (selected) ->
                $log.log("selecting this node! #{selected}")
                angular.forEach(this.nodes, (node) ->
                    if node.active and node isnt selected
                        node.active = false
                )
                selected.active = true
        ]
        return {
            bindToController: {
                # addNode: '&'
                heading: '@'
                nodes: '=nodes'
                select: '&'
            }
            controller: controller
            controllerAs: 'nodeset'
            restrict: 'E'
            scope: {}
            template: template
            transclude: true
        }
    )
    app.directive('foundNode', () ->
        template = '
          <div role="tabpanel" ng-show="active" ng-transclude>
          </div>
        '

        link = (scope, element, attrs, ctrl) ->
            console.log('add', ctrl.addNode)
            console.log('select', ctrl.select)
            scope.active = false
            ctrl.addNode(scope)
            ctrl.select(scope)

        return {
            link: link
            restrict: 'E'
            require: '^foundNodeset'
            scope: {
                heading: '@'
            }
            template: template
            transclude: true
        }
    )

    app.controller(
        'nosferatuController',
        ['$scope', '$log', '$http', '$timeout', ($scope, $log, $http, $timeout) ->
            console.log('beginning of main controller')
            submitButtonTexts = {false: 'Search for Node', true: 'Loading...'}
            $scope.findingNodes = false
            $scope.submitButtonText = submitButtonTexts[$scope.findingNodes]
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
                        $log.log("  find-nodes", results)
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
