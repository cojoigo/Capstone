angular.module('nosferatuApp').directive('ruleSelector', () ->
    controller = ['$scope', '$log', '$http', '$timeout', ($scope, $log, $http, $timeout) ->
        self = this

        @enableAddRuleBtn = () ->
            result = (
                (not @ruleName) or
                (not @daysOfWeekSelected.length) or
                (if @ruleType is 'Schedule' then (if (@scheduleTimeType is 'auto') then (not @scheduleZipCode) else false) else false) or
                (if @ruleType is 'Event' then (not @foreignNode) else false)
            )
            return result

        @ruleTypes = ['Schedule', 'Event']
        @daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        am_pm = (i) ->
            if i < 12
                return 'AM'
            else
                return 'PM'
        @hoursInDay = {}
        for i in [0..24]
            str = "#{((i + 11) % 12) + 1} #{am_pm(i)}"
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

        @ruleTurnOn = 'unchanged'
        @ruleMotionTurnOn = 'unchanged'

        @foreignNode = @foreignNodes[0]
        @foreignNodeStatus = 'on'

        @eventNode = (node) ->
            if node?
                $log.log(" - node from node name", node)
                return node.id
            return null

        @addRule = () ->
            $log.log('Adding the rule')
            data = {
                'name': @ruleName
                'type': @ruleType
                'turn_on': @ruleTurnOn
                'turn_motion_on': @ruleMotionTurnOn
                'days': @daysOfWeekSelected
                'sched_type': @scheduleTimeType

                # manual
                'hour': @hoursInDay[@hourInDay]
                'minute': @minuteInDay

                # auto
                'zip_code': @scheduleZipCode or ''
                'time_of_day': @scheduleTimeOfDayType

                'event_node': self.eventNode(self.foreignNode)
                'event_node_status': self.foreignNodeStatus or null
            }

            $http.post("/nodes/#{@node.id}/rules", data).then((results) ->
                $log.log("  - success: ", results.data)
                self.addedRules.push(results.data)
            ).catch(errFunc)

        return
    ]
    return {
        bindToController: {
            foreignNodes: '='
            node: '='
            addedRules: '='

            ruleName: '='
            ruleTypes: '='
            ruleType: '='
            scheduleTimeType: '='
            scheduleZipCode: '='
            scheduleTimeOfDayType: '='

            scheduleTimeTypeChange: '&'
        }
        controller: controller
        controllerAs: 'rs'
        restrict: 'E'
        scope: {}
        templateUrl: './static/templates/rule-selector.html'
    }
)
