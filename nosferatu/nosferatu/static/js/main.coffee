(() ->
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
                    if results.status == 202
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
                    ip: this.ip,
                    mac: this.mac,
                    name: this.name or '',
                }
                console.log('SENF', sendInfo)
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
                                $log.log("    - success: ", self.addedNodes, results.data.id)

                                self.addedNodes.push(results.data.id)
                                console.log('    - data', self.addedNodes)

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

            return
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
                    'turn_on': @ruleTurnOn
                    'days': @daysOfWeekSelected
                    'schedule_type': @scheduleTimeType

                    # manual
                    'hour': @hoursInDay[@hourInDay]
                    'minute': @minuteInDay

                    # auto
                    'zip_code': @scheduleZipCode or ''
                    'time_of_day': @scheduleTimeOfDayType
                }

                $http.post("/nodes/#{@node.id}/rules", data).then(
                    ((results) ->
                        $log.log(" - job: #{results.data}")
                        self.addRulePoll(results.data)
                    ),
                    ((error) ->
                        $log.log(error)
                    )
                )

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
                    $log.log(" - /nodes/#{self.node.id}/rules", count)
                    $http.get("/nodes/#{self.node.id}/rules", config).then(
                        ((results) ->
                            if results.status == 202
                                $log.log("  - failed:", results.data)
                                count += 1
                                if count is 3
                                    $timeout.cancel(timeout)
                                    return false
                            else if results.status == 200
                                $log.log("  - success: ", results.data)

                                self.addedRules.push(results.data)

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

            return
        ]
        return {
            bindToController: {
                node: '='
                addedRules: '='

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

    app.directive('rulesList', () ->
        template = '''
          <h1>Existing Rules</h1>
          <table>
          <tr>
            <td><b>Delete</b></td>
            <td><b>Name</b></td>
            <td><b>Turn On</b></td>
            <td><b>Days</b></td>
          </tr>
          <tr ng-repeat="rule in rlist.rules">
            <td>
              <button type="submit" class="btn btn-default" ng-click="rlist.delete(rule.id)">
                Delete
              </button>
            </td>
            <td>
              {[rule.name]}
            </td>
            <td>
              {[rule.turn_on]}
            <td>
              {[rule.days]}
            </td>
          </tr>
          </table>
        '''
        controller = ['$scope', '$log', '$http', '$timeout', ($scope, $log, $http, $timeout) ->
            $log.log('Beginning of rules List directive controller', @node.id)
            self = this

            @delete = (rule_id) ->
                $log.log("Deleting rule #{rule_id}")

                $http.delete("/nodes/#{self.node.id}/rules/#{rule_id}").then(
                    ((results) ->
                        $log.log(' - deleted successfully', results.data)

                        delete self.rules[results.data.result]

                        $log.log(' - new rules, ', self.rules)
                    ), errFunc
                )

            return
        ]
        return {
            bindToController: {
                node: '='
                rules: '='
            }
            controller: controller
            controllerAs: 'rlist'
            restrict: 'E'
            scope: {}
            template: template
            # templateUrl: './static/templates/rules-list.html'
        }
    )

    app.controller(
        'nosferatuController',
        ['$scope', '$log', '$http', '$timeout', ($scope, $log, $http, $timeout) ->
            console.log('beginning of main controller')
            self = this
            submitButtonTexts = {false: 'Search for Node', true: 'Loading...'}
            this.findingNodes = false
            this.submitButtonText = submitButtonTexts[this.findingNodes]

            this.addedNodes = []

            this.nodes = {}
            this.foundNodes = {}

            $scope.$watchCollection(
                angular.bind(this, () -> return this.addedNodes),
                ((newValue, oldValue) ->
                    $log.log("      - new: '#{newValue}', old: '#{oldValue}'")
                    newDiff = []
                    for obj in newValue
                        if obj not in oldValue
                            newDiff.push(obj)

                    for id in newDiff
                        $log.log("Get node: #{id}")
                        self.getNode(id)
                )
            )

            this.populateInitialNodes = () ->
                $log.log('Getting existing initial nodes')

                $http.get('/nodes/get').then(
                    ((results) ->
                        $log.log(' - id', results.data)
                        self.populateInitialNodesPoll(results.data)
                    ),
                    errFunc
                )
            this.populateInitialNodes()

            this.populateInitialNodesPoll = (jobId) ->
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
                                    self.getNode(id)

                                $timeout.cancel(timeout)
                                return false

                            # Continue to call the poller every 2 seconds until its canceled
                            timeout = $timeout(poller, 2000)
                        ),
                        errFunc
                    )
                poller()
            this.getNode = (id) ->
                $http.get("/nodes/#{id}").then(
                    ((results) ->
                        $log.log(" - job: #{results.data}")
                        self.getNodePoll(id, results.data)
                    ),
                    errFunc
                )

            this.getNodePoll = (id, jobId) ->
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
                                self.nodes[results.data.id] = results.data

                                # Its added now, so doesnt need to be found
                                $log.log(self.foundNodes)
                                delete self.foundNodes[results.data.mac]
                                console.log('      - data', self.nodes)

                                # Reset the button to search for more nodes now
                                if self.foundNodes.length == 0
                                    self.findingNodes = false
                                self.submitButtonText = submitButtonTexts[self.findingNodes]

                                $timeout.cancel(timeout)
                                return false

                            # Continue to call the poller every 2 seconds until its canceled
                            timeout = $timeout(poller, 2000)
                        ),
                        errFunc
                    )
                poller()

            this.findNodes = () ->
                $log.log('Searching for new nodes')

                $http.get('/nodes/find').then(
                    ((results) ->
                        $log.log(' - id', results.data)
                        self.findNodesPoll(results.data)
                        self.findingNodes = true
                        self.submitButtonText = submitButtonTexts[self.findingNodes]
                    ),
                    errFunc
                )

            this.findNodesPoll = (jobId) ->
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
                                    self.foundNodes[mac] = results.data[mac]
                                console.log('     - data', self.foundNodes)

                                if self.foundNodes.length == 0
                                    self.findingNodes = false
                                self.submitButtonText = submitButtonTexts[self.findingNodes]
                                $timeout.cancel(timeout)
                                return false
                            else
                                self.findingNodes = false
                                self.submitButtonText = submitButtonTexts[self.findingNodes]

                            # Continue to call the poller every 2 seconds until its canceled
                            timeout = $timeout(poller, 2000)
                        ),
                        ((error) ->
                            $log.log(error)
                            self.findingNodes = false
                            self.submitButtonText = submitButtonTexts[self.findingNodes]
                        )
                    )
                poller()

            return
        ]
    )

    app.controller(
        'nodeSettingsController',
        ['$scope', '$log', '$http', '$timeout', ($scope, $log, $http, $timeout) ->
            console.log('beginning of settings controller')

            self = this

            @node = $scope.$parent.node
            @rules = {}
            @addedRules = []
            @deleted = false

            $scope.$watchCollection(
                angular.bind(this, () -> return @addedRules),
                ((newValue, oldValue) ->
                    $log.log('Added Rules')
                    $log.log("      - new: '#{newValue}', old: '#{oldValue}'")
                    newDiff = []
                    for obj in newValue
                        if obj not in oldValue
                            newDiff.push(obj)

                    $log.log(newDiff)

                    for id in newDiff
                        $log.log("Get node: ", id.id)
                        self.getRule(id.id)
                )
            )

            @delete = (nodes) ->
                $log.log("Toggling the node! #{self.node.id}")

                $http.delete("/nodes/#{self.node.id}").then(
                    ((results) ->
                        $log.log(' - deleted successfully', results.data)

                        delete nodes[results.data.result]
                        self.deleted = true

                        $log.log(' - new rules, ', nodes)
                    ), errFunc
                )

            @toggle = () ->
                $log.log("Toggling the node status #{self.node.id}")

                $http.post("/nodes/#{self.node.id}/toggle").then(
                    ((results) ->
                        $log.log(' - toggled successfully', results.data)
                    ), errFunc
                )

            @getRule = (id) ->
                $log.log("Getting the rule, #{id}")
                $http.post("/nodes/#{self.node.id}/rules/#{id}").then(
                    ((results) ->
                        $log.log(" - job: #{results.data}")
                        return [id, results.data]
                    ),
                    errFunc
                ).then(
                    ((input) ->
                        [id, jobId] = input
                        success = (results) ->
                            $log.log("  - success: ", results)
                            self.rules[results.id] = results

                            # Its added now, so doesnt need to be found
                            delete self.addedRules[results.id]
                            $log.log("All the rules", self.rules)

                        config = {
                            params: {
                                job_id: jobId
                            }
                        }
                        pollFunc($http.get("/nodes/#{self.node.id}/rules/#{id}", config), success, $timeout, $log)
                    ),
                    errFunc
                )

            @getRules = () ->
                $log.log("Getting the rules")
                $http.post("/nodes/#{self.node.id}/rules/all").then(
                    ((results) ->
                        $log.log("rules gotten ", results.data)
                        return results.data
                    ), errFunc
                ).then(
                    ((jobId) ->
                        $log.log('  - job id', jobId)
                        config = {
                            params: {
                                'job_id': jobId
                            }
                        }
                        data = {
                            'job_id': jobId
                        }
                        $http.get("/nodes/#{self.node.id}/rules/all", config).then(
                            ((results) ->
                                $log.log(' - gotten rules: ', results.data)
                                for id, rule of results.data
                                    $log.log(' - ', id, rule)
                                    self.getRule(rule)
                            ), errFunc
                        )
                    )
                )
            @getRules()

            @checkNodeStatus = () ->
                time = ''
                poller = () ->
                    $log.log("Checking Node(#{self.node.id})'s status'")
                    $http.get("/nodes/#{self.node.id}/status").then(
                        ((results) ->
                            if self.deleted
                                return false
                            if results.status == 202
                                $log.log("  - failed:", results.data)
                            else if results.status == 200
                                $log.log(" - ", results.data)
                                self.relayStatus = results.data.relay
                                if results.data.relay != 'Error'
                                    date = new Date()
                                    self.lastUpdate = date.toLocaleString()

                            # Continue to call the poller every 2 seconds until its canceled
                            time = $timeout(poller, 5000)
                        ), errFunc
                    )
                poller()
            @checkNodeStatus()

            return
        ]
    )
)()
