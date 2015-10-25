(() ->
    angular.directive('nosferatuApp.ruleSelector', () ->
        controller = ['$scope', '$log', '$http', '$timeout', ($scope, $log, $http, $timeout) ->
            $log.log('Beginning of ruleSelector directive controller')

            self = this

            @enableAddRuleBtn = () ->
                a = not (@ruleName and @days and (@scheduleZipCode if @scheduleTimeType))
                $log.log("diabling the button? #{a}")
                return (not @ruleName) or (not @days) or ((not @scheduleZipCode) if @scheduleTimeType)

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

            @updateRuleTypes = () ->
                $log.log('Updating rule types')
                $log.log(" - rule type is #{@ruleType}")
            @updateRuleTypes()

            @addRule = () ->
                $log.log('Adding the rule')
                $log.log(" - Name: #{@ruleName}")
                $log.log(" - Type: #{@ruleType}")
                $log.log(" - Turn On: #{@ruleTurnOn}")
                $log.log(" - Days: #{@daysOfWeekSelected}")
                $log.log(" - Hour:minute: #{@hoursInDay[@hourInDay]}:#{@minuteInDay}")
                $log.log(" - ScheduleType: #{@scheduleTimeType}")
                $log.log(" - ZipCode: #{@scheduleZipCode}")
                $log.log(" - TimeOfDay: #{@scheduleTimeOfDayType}")
            @addRule()
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
                updateRuleTypes: '&'
            }
            controller: controller
            controllerAs: 'rselect'
            restrict: 'E'
            scope: {}
            templateUrl: './static/templates/rule-selector.html'
        }
    )
)()
