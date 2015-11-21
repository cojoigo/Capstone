angular.module('nosferatuApp').directive('foundNode', () ->
    controller = ['$scope', '$log', '$http', '$timeout', ($scope, $log, $http, $timeout) ->
        $log.log('Beginning of foundNode directive controller')

        self = this

        @testBtnTexts = {false: 'Test', true: 'Stop'}
        @updateTestText = (value) ->
            self.testing = value
            self.testBtnText = self.testBtnTexts[self.testing]
        @updateTestText(false)

        @saveBtnTexts = {false: 'Save', true: '...'}
        @updateSaveText = (value) =>
            self.saving = value
            self.saveBtnText = @saveBtnTexts[self.saving]
        @updateSaveText(false)

        @test = () ->
            $log.log("Testing node #{self.node.ip}")
            action = 'start'
            if self.testing
                action = 'stop'

            self.updateTestText(not self.testing)
            data = {
                action: action,
                ip: self.node.ip,
                mac: self.node.mac,
            }
            $http.post('/nodes/test', data)

        @add = () ->
            if not self.name?
                return

            $log.log("Saving node #{self.node.ip}", self)

            self.updateSaveText(true)
            sendInfo = {
                ip: self.node.ip,
                mac: self.node.mac,
                name: self.name,
            }
            console.log('SEND', sendInfo)
            $http.post('/nodes/add', sendInfo).then((results) ->
                $log.log("  - success: ", self.addedNodes, results.data.id)
                self.addedNodes.push(results.data.id)
                console.log('    - data', self.addedNodes)
            )
            .catch(errFunc)

        return
    ]

    return {
        bindToController: {
            node: '='
            addedNodes: '='

            name: '='
        }
        controller: controller
        controllerAs: 'fn'
        restrict: 'E'
        scope: {}
        templateUrl: './static/templates/found-node.html'
    }
)
