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
        controller = ['$scope', '$log', '$http', '$timeout', ($scope, $log, $http, $timeout) ->
            $log.log('Beginning of ruleSelector directive controller', @node.id)

            self = this

            @enableAddRuleBtn = () ->
                result = (
                    (not @ruleName) or
                    (not @daysOfWeekSelected.length) or
                    (if (@scheduleTimeType is 'auto') then (not @scheduleZipCode?) else false)
                )
                $log.log("diabling the button? #{result}")
                return result

            @ruleTypes = ['Schedule', 'Event', 'Motion']
            @daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            am_pm = (i) ->
                if i < 12
                    return 'AM'
                else
                    return 'PM'
            @hoursInDay = {}
            for i in [0..24]
                str = "#{((i + 11) % 12) + 1}:00 #{am_pm(i)}"
                @hoursInDay[str] = i
            @hoursInDayArr = Object.keys(@hoursInDay)
            @minutesInDay = [0, 15, 30, 45]

            @ruleType = @ruleTypes[0]

            @daysOfWeekSelected = []
            @daysOfWeekToggle = (day) ->
                id = @daysOfWeekSelected.indexOf(day)
                if id > -1
                    @daysOfWeekSelected.splice(id, 1)
                else
                    @daysOfWeekSelected.push(day)

            @scheduleTimeType = 'manual'
            @scheduleTimeOfDayType = 'sunrise'
            @hourInDay = @hoursInDayArr[0]
            @minuteInDay = @minutesInDay[0]

            @ruleTurnOn = true
            @ruleTurnOnStr = 'On'
            @scheduleActionChange = () ->
                if @ruleTurnOn
                    @ruleTurnOnStr = 'On'
                else
                    @ruleTurnOnStr = 'Off'

            @addRule = (real) ->
                if not real?
                    return

                $log.log('Adding the rule')
                data = {
                    'name': @ruleName
                    'type': @ruleType
                    'action': @ruleTurnOn
                    'days': @daysOfWeekSelected
                    'schedule_type': @scheduleTimeType

                    # manual
                    'hour': @hoursInDay[@hourInDay]
                    'minute': @minuteInDay

                    # auto
                    'zip_code': @scheduleZipCode
                    'time_of_day': @scheduleTimeOfDayType
                }

                $http.post("/nodes/#{@node.id}/rule", data).then(
                    ((results) ->
                        $log.log(" - job: #{results.data}")
                        self.addRulePoll(results.data)
                    ),
                    ((error) ->
                        $log.log(error)
                    )
                )
            @addRule()

            @addRulePoll = (jobId) ->
                if not jobId?
                    return

                timeout = ''
                count = 0
                poller = () ->
                    config = {
                        params: {
                            'job_id': jobId
                        }
                    }
                    $log.log(" - /nodes/#{self.node.id}/rule", count)
                    $http.get("/nodes/#{self.node.id}/rule", config).then(
                        ((results) ->
                            if results.status == 202
                                $log.log("  - failed:", results.data)
                                count += 1
                                if count is 3
                                    $timeout.cancel(timeout)
                                    return false
                            else if results.status == 200
                                $log.log("  - success: ", results.data)

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
            @addRulePoll()
        ]
        return {
            bindToController: {
                node: '='
                ruleName: '='
                ruleTypes: '='
                ruleType: '='
                scheduleTimeType: '='
                scheduleZipCode: '='
                scheduleTimeOfDayType: '='

                addRule: '&'
                scheduleTimeTypeChange: '&'
                enableAddRuleBtn: '&'
            }
            controller: controller
            controllerAs: 'rselect'
            restrict: 'E'
            scope: {}
            templateUrl: './static/templates/rule-selector.html'
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
