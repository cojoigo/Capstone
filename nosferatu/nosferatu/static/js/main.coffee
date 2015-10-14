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
            @updateTestText(@node)

            ((that) =>
                that.saving = false
                @saveBtnTexts = {false: 'Save', true: '...'}
                @updateSaveText = (that, value) =>
                    that.saving = value
                    that.saveBtnText = @saveBtnTexts[that.saving]
                @updateSaveText(that, false)

                $log.log(" - Initialize the save to #{that.saving}, value is #{@saveBtnText}")
            )(@node)

            @node.test = () ->
                $log.log("Testing node #{this.id}")
                action = 'start'
                if self.testing
                    action = 'stop'

                $log.log(' - testing', self.testBtnTexts[self.testing])
                $log.log(" - /nodes/#{this.id}/test/#{action}")

                self.testing = not self.testing
                self.updateTestText(this)
                $http.get("/nodes/#{this.id}/test/#{action}")

            @node.add = () ->
                $log.log("Saving node #{this.id}", this)

                self.updateSaveText(this, true)
                sendInfo = {
                    'id': this.id
                    'ip': this.ip
                    'mac': this.mac
                    'name': this.name
                }
                $http.post('/nodes/add/', sendInfo).then(
                    ((results) ->
                        $log.log(" - add node", results.data)
                        self.addPoll(results.data)
                    ),
                    ((error) ->
                        $log.log(error)
                    )
                )

            @addPoll = (jobId) ->
                timeout = ''
                count = 0
                poller = () =>
                    $log.log(" - /nodes/add/#{jobId}", count)
                    $http.get("/nodes/add/#{jobId}").then(
                        ((results) ->
                            if results.status == 202
                                $log.log("    - failed:", results.data)
                                count += 1
                                if count is 3
                                    $log.log("    - Failed, done")
                                    self.updateSaveText(this, false)

                                    $timeout.cancel(timeout)
                                    return false
                            else if results.status == 200
                                $log.log("    - success: ", $scope.$parent.addedNodes, results.data.id)

                                $scope.$parent.addedNodes.push(results.data.id)
                                console.log('    - data', $scope.$parent.addedNodes)

                                $timeout.cancel(timeout)
                                return false


                            # Continue to call the poller every 2 seconds until its canceled
                            timeout = $timeout(poller, 1000)
                        ),
                        ((error) ->
                            count += 1
                            $log.log(error)
                        )
                    )
                poller()
        ]

        return {
            bindToController: {
                add: '&'
                node: '=node'
                addedNodes: '='
                testBtnText: '='
                saveBtnText: '='
                saving: '='
            }
            controller: controller
            controllerAs: 'foundnode'
            restrict: 'E'
            scope: {}
            template: template
            transclude: true
        }
    )

    app.directive('ruleSelector', () ->
        template = '''
            <form role="form" ng-submit="addRule()">
              <h1>Add a rule</h1>
              <div class="row">
                <div class="small-4 columns">
                  <label>Rule Name</label>
                  <input type="text" placeholder="Rule Name" />
                </div>
                <div class="small-4 columns">
                  <label>Rule Type</label>
                  <select ng-options="type for type in rselect.ruleTypes"
                          ng-model="rselect.ruleType"
                          ng-change="rselect.updateRuleTypes()"
                  ></select>
                </div>
                <div class="small-4 columns">
                  <button type="submit" class="btn btn-default">Add</button>
                </div>
              </div>
              <div class="row" ng-show="rselect.ruleType === 'Schedule'">
                <div class="small-4 columns">
                  <div ng-repeat="day in rselect.daysOfWeek">
                    <input id="dayOfWeek{[day]}" type="checkbox">
                      <label for="dayOfWeek{[day]}">
                        {[day]}
                      </label>
                    </input>
                    <br />
                  </div>
                </div>
                <div class="small-4 columns">
                  <label>Hour</label>
                  <select ng-options="day for day in rselect.hoursInDay"
                          ng-model="rselect.hourInDay"
                  ></select>
                  <br />

                  <label>Minute</label>
                  <select ng-options="minute for minute in rselect.minutesInDay"
                          ng-model="rselect.minuteInDay"
                  ></select>
                  <br />

                  <label>Turn On/Off</label>
                  <input id="ruleAddTurnOn" type="checkbox"></input>
                </div>
                <div class="small-4 columns">
                </div>
              </div>
            </form>
        '''

        controller = ['$scope', '$log', '$http', '$timeout', ($scope, $log, $http, $timeout) ->
            $log.log('Beginning of ruleSelector directive controller')

            self = this

            @ruleTypes = ['Schedule', 'Time of Day', 'Event']
            @ruleType = @ruleTypes[0]

            @daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

            @hoursInDay = (i for i in [1..24])
            @hourInDay = @hoursInDay[0]

            @minutesInDay = [0, 15, 30, 45]
            @minuteInDay = @minutesInDay[0]

            @updateRuleTypes = () ->
                $log.log('Updating rule types')
                $log.log(" - rule type is #{@ruleType}")
            @updateRuleTypes()

            @addRule = () ->
                $log.log('Adding the rule')
            @addRule()
        ]
        return {
            bindToController: {
                node: '='
                ruleTypes: '='
                ruleType: '='
                updateRuleTypes: '&'
                addRule: '&'
            }
            controller: controller
            controllerAs: 'rselect'
            restrict: 'E'
            scope: {}
            template: template
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
            $scope.foundNodes = {}

            $scope.$watchCollection(
                'addedNodes',
                ((newValue, oldValue) ->
                    $log.log("      - new: '#{newValue}', old: '#{oldValue}'")
                    newDiff = []
                    for obj in newValue
                        if obj not in oldValue
                            newDiff.push(obj)

                    for id in newDiff
                        $log.log("Get node: #{id}")
                        $scope.getNode(id)
                )
            )

            $scope.populateInitialNodes = () ->
                $log.log('Getting existing initial nodes')

                $http.get('/nodes/get').then(
                    ((results) ->
                        $log.log(' - id', results.data)
                        $scope.populateInitialNodesPoll(results.data)
                    ),
                    ((error) ->
                        $log.log(error)
                    )
                )
            $scope.populateInitialNodes()

            $scope.populateInitialNodesPoll = (jobId) ->
                timeout = ''
                count = 0
                poller = () ->
                    $log.log(" - /nodes/get/#{jobId}", count)
                    $http.get("/nodes/get/#{jobId}").then(
                        ((results) ->
                            if results.status == 202
                                $log.log("  - failed:", results.data)
                                count += 1
                                if count is 3
                                    $timeout.cancel(timeout)
                                    return false
                            else if results.status == 200
                                $log.log("  - success: ", results.data)
                                for key, id of results.data
                                    $scope.getNode(id)

                                $timeout.cancel(timeout)
                                return false

                            # Continue to call the poller every 2 seconds until its canceled
                            timeout = $timeout(poller, 2000)
                        ),
                        ((error) ->
                            $log.log(error)
                        )
                    )
                poller()
            $scope.getNode = (id) ->
                $http.get("/nodes/#{id}").then(
                    ((results) ->
                        $log.log(" - job: #{results.data}")
                        $scope.getNodePoll(id, results.data)
                    ),
                    ((error) ->
                        $log.log(error)
                    )
                )

            $scope.getNodePoll = (id, jobId) ->
                timeout = ''
                count = 0
                poller = () ->
                    $log.log(" - /nodes/#{id}/jobs/#{jobId}", count)
                    $http.get("/nodes/#{id}/jobs/#{jobId}").then(
                        ((results) ->
                            if results.status == 202
                                $log.log("  - failed:", results.data)
                                count += 1
                                if count is 3
                                    $timeout.cancel(timeout)
                                    return false
                            else if results.status == 200
                                $log.log("  - success: ", results.data)
                                $scope.nodes.push(results.data)

                                # Its added now, so doesnt need to be found
                                $log.log($scope.foundNodes)
                                delete $scope.foundNodes[results.data.mac]
                                console.log('      - data', $scope.nodes)

                                # Reset the button to search for more nodes now
                                if $scope.foundNodes.length == 0
                                    $scope.findingNodes = false
                                $scope.submitButtonText = submitButtonTexts[$scope.findingNodes]

                                $timeout.cancel(timeout)
                                return false

                            # Continue to call the poller every 2 seconds until its canceled
                            timeout = $timeout(poller, 2000)
                        ),
                        ((error) ->
                            $log.log(error)
                        )
                    )
                poller()

            $scope.findNodes = () ->
                $log.log('Searching for new nodes')

                $http.get('/nodes/find').then(
                    ((results) ->
                        $log.log(' - id', results.data)
                        $scope.findNodesPoll(results.data)
                        $scope.findingNodes = true
                        $scope.submitButtonText = submitButtonTexts[$scope.findingNodes]
                    ),
                    ((error) ->
                        $log.log(error)
                    )
                )

            $scope.findNodesPoll = (jobId) ->
                timeout = ''
                count = 0
                poller = () ->
                    $log.log(' - /nodes/find/' + jobId, count)
                    $http.get('/nodes/find/' + jobId).then(
                        ((results) ->
                            if results.status == 202
                                $log.log("   - failed:", results)
                                count += 1
                                if count is 3
                                    $timeout.cancel(timeout)
                                    return false
                            else if results.status == 200
                                $log.log("   - success: ", results.data)
                                for mac, item of results.data
                                    $scope.foundNodes[mac] = results.data[mac]
                                console.log('     - data', $scope.foundNodes)

                                if $scope.foundNodes.length == 0
                                    $scope.findingNodes = false
                                $scope.submitButtonText = submitButtonTexts[$scope.findingNodes]
                                $timeout.cancel(timeout)
                                return false
                            else
                                $scope.findingNodes = false
                                $scope.submitButtonText = submitButtonTexts[$scope.findingNodes]

                            # Continue to call the poller every 2 seconds until its canceled
                            timeout = $timeout(poller, 2000)
                        ),
                        ((error) ->
                            $log.log(error)
                            $scope.findingNodes = false
                            $scope.submitButtonText = submitButtonTexts[$scope.findingNodes]
                        )
                    )
                poller()
        ]
    )
)()
