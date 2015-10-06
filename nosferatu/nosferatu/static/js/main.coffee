(() ->
    app = angular.module('nosferatuApp', ['mm.foundation'])
    app.config(['$interpolateProvider', ($interpolateProvider) ->
        $interpolateProvider.startSymbol('{[')
        $interpolateProvider.endSymbol(']}')
    ])
    app.directive('foundNode', () ->
        template = '<div ng-transclude></div>'

        controller = ['$scope', '$log', '$http', '$timeout', ($scope, $log, $http, $timeout) ->
            $log.log('Beginning of foundNode directive controller')

            self = this
            @node.testBtnText = 'Test'

            @updateTestText = (t) ->
                t.testBtnText = self.testBtnTexts[self.testing]

            @testing = false
            @testBtnTexts = {false: 'Test', true: 'Stop'}
            console.log('asdf', @node.testBtnText)
            @updateTestText(@node)

            @adding = false
            @addingBtnTexts = {false: 'Save', true: '...'}
            @addingBtnText = @addingBtnTexts[@adding]

            @node.test = () ->
                $log.log("Testing node #{this.id}")
                action = 'start'
                if not self.testing
                    action = 'stop'
                self.testing = not self.testing
                console.log('thisL', this, self.testBtnTexts[self.testing])
                self.updateTestText(this)

                $http.get("/nodes/#{this.id}/test/#{action}")

            @node.add = () ->
                $log.log("Adding node #{this.id}")

                sendInfo = {
                    'id': this.id
                    'ip': this.ip
                    'mac': this.mac
                    'name': this.name
                }
                $http.post('/nodes/add/', sendInfo).then(
                    ((results) ->
                        $log.log("  find-nodes", results)
                        self.addPoll(results)
                        self.adding= true
                        self.addingBtnText = self.addingBtnTexts[self.adding]
                    ),
                    ((error) ->
                        $log.log(error)
                    )
                )

            @addPoll = (jobId) ->
                timeout = ''
                poller = () ->
                    $log.log('/nodes/add/' + jobId)
                    $http.get('/nodes/add/' + jobId)
                        .success((data, status, headers, config) ->
                            if status == 202
                                $log.log("  failed:", data, status)
                                self.added = false
                                self.addingBtnText = self.addingBtnTexts[self.adding]
                            else if status == 200
                                $log.log("  success: ", $scope.$parent.addedNodes, data)
                                $scope.$parent.addedNodes.push(data)
                                console.log('    data', $scope.$parent.addedNodes)

                                $timeout.cancel(timeout)
                                return false

                            # Continue to call the poller every 2 seconds until its canceled
                            timeout = $timeout(poller, 2000)
                        )
                poller()
                $log.log("Adding node #{this.id}")
        ]

        return {
            bindToController: {
                add: '&'
                node: '=node'
                addedNodes: '='
                testBtnText: '='
            }
            controller: controller
            controllerAs: 'foundnode'
            restrict: 'E'
            scope: {}
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

            $scope.addedNodes = []

            $scope.nodes = []
            $scope.foundNodes = []

            $scope.$watchCollection(
                'addedNodes',
                ((newValue, oldValue) ->
                    $log.log("new and old: #{newValue}")
                    $log.log("new and old: #{oldValue}")
                    newDiff = []
                    for obj in newValue
                        if obj not in oldValue
                            newDiff.push(obj.id)
                    for id in newDiff
                        $log.log("Get node: #{id}")
                        $http.get("/nodes/#{id}")
                            .success((results) ->
                                $log.log("  - job: ", results)
                                $scope.getNodePoll(results)
                            )
                            .error((error) ->
                                $log.log(error)
                            )
                )
            )

            $scope.getNodePoll = (jobId) ->
                timeout = ''
                poller = () ->
                    $log.log('/nodes/get/' + jobId)
                    $http.get('/nodes/get/' + jobId)
                        .success((data, status, headers, config) ->
                            if status == 202
                                $log.log("   failed:", data, status)
                            else if status == 200
                                $log.log("  success: ", data)
                                $scope.nodes.push(data)

                                # Its added now, so doesnt need to be found
                                for item in $scope.foundNodes
                                    if item.id == data.id
                                        console.log('asdf;lkj', item.id, data.id, item, data)
                                        $scope.foundNodes.pop(item)
                                console.log('  - data', $scope.nodes)

                                # Reset the button to search for more nodes now
                                if $scope.foundNodes.length == 0
                                    $scope.findingNodes = false
                                $scope.submitButtonText = submitButtonTexts[$scope.findingNodes]

                                $timeout.cancel(timeout)
                                return false

                            # Continue to call the poller every 2 seconds until its canceled
                            timeout = $timeout(poller, 2000)
                        )
                poller()

            $scope.findNodes = () ->
                $log.log('Searching for new nodes')

                $http.get('/nodes/find')
                    .success((results) ->
                        $log.log('  - ', results)
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
                    $log.log('/nodes/find/' + jobId)
                    $http.get('/nodes/find/' + jobId)
                        .success((data, status, headers, config) ->
                            if status == 202
                                $log.log("  failed:", data, status)
                            else if status == 200
                                $log.log("  success: ", data.items)
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
