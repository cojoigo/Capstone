angular.module('nosferatuApp').directive('rulesList', () ->
    controller = ['$scope', '$log', '$http', ($scope, $log, $http) ->
        self = this

        @delete = (rule_id) ->
            $log.log("Deleting rule #{rule_id}")

            $http.delete("/nodes/#{self.node.id}/rules/#{rule_id}").then((results) ->
                $log.log(' - deleted successfully', results.data)
                delete self.rules[results.data.result]
                $log.log(' - new rules, ', self.rules)
            ).catch(errFunc)

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
        templateUrl: './static/templates/rules-list.html'
    }
)
