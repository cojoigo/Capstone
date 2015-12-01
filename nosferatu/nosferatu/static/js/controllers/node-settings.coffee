angular.module('nosferatuApp').controller('nodeSettingsController',
    ['$scope', '$log', '$http', '$timeout', ($scope, $log, $http, $timeout) ->
        self = this

        @node = $scope.$parent.node
        @rules = {}
        @addedRules = []
        @motionStatus = 'Off'
        @relayStatus = false
        @MotionTimeout = 5
        @newMotionTimeout = ''

        $scope.$watchCollection(
            angular.bind(this, () -> return @addedRules),
            ((newValue, oldValue) ->
                $log.log('Added Rules')
                $log.log("      - new", newValue, 'old', oldValue)
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

        @toggle = () ->
            $log.log("Toggling the node status #{self.node.id}")

            $http.post("/nodes/#{self.node.id}/toggle").then((results) ->
                $log.log(' - toggled successfully', results.data)
            ).catch(errFunc)

        @changeMotion = () ->
            $log.log("Changing motion setting, #{self.node.id}")

            if self.motionStatus is 'Off'
                status = 'On'
            else
                status = 'Off'

            data = {
                'motion': status,
            }
            if self.newMotionTimeout isnt self.motionTimeout
                data['motion_timeout'] = self.newMotionTimeout

            $http.post("/nodes/#{self.node.id}/motion", data).then((results) ->
                $log.log("Motion should be changed")
            ).catch(errFunc)

        @getRule = (id) ->
            $log.log("Getting the rule, #{id}")
            $http.get("/nodes/#{self.node.id}/rules/#{id}").then((results) ->
                $log.log("  - success: ", results.data)
                self.rules[results.data.id] = results.data

                # Its added now, so doesnt need to be found
                delete self.addedRules[results.data.id]
                $log.log("All the rules", self.rules)
            ).catch(errFunc)

        @getRules = () ->
            $log.log("Getting the rules")
            $http.get("/nodes/#{self.node.id}/rules").then((results) ->
                $log.log("rules gotten ", results.data)
                for id, rule of results.data
                    $log.log(' - ', id, rule)
                    self.getRule(rule)
            ).catch(errFunc)
        @getRules()

        @checkNodeStatus = () ->
            # if not self.node.active? or self.node.active
            #     return
            time = ''
            poller = () ->
                $log.log("Checking Node(#{self.node.id})'s status'")
                $http.get("/nodes/#{self.node.id}/status").then(
                    ((results) ->
                        if self.node.deleted
                            return false
                        if results.status == 202
                            $log.log("  - failed:", results.data)
                        else if results.status == 200
                            $log.log(" - ", results.data)
                            self.relayStatus = results.data.relay is 'On'
                            if results.data.relay != 'Error'
                                date = new Date()
                                self.lastUpdate = date.toLocaleString()
                                self.motionStatus = results.data.motion
                                self.motionTimeout = results.data.motionTimeout

                        # Continue to call the poller every 5 seconds until its canceled
                        time = $timeout(poller, 1000)
                    ), errFunc
                )
            poller()
        @checkNodeStatus()

        return
    ]
)
