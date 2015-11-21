angular.module('nosferatuApp').controller('mainController',
    ['$scope', '$log', '$http', '$timeout', ($scope, $log, $http, $timeout) ->
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
                $log.log(' - new:', newValue, 'old', oldValue)
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

            $http.get('/nodes/get').then((results) ->
                $log.log("  - success: ", results.data)
                for key, id of results.data
                    self.getNode(id)
            ).catch(errFunc)
        this.populateInitialNodes()

        this.getNode = (id) ->
            $http.get("/nodes/#{id}").then((results) ->
                $log.log("  - success: ", results.data)
                self.nodes[results.data.id] = results.data
                self.nodes[results.data.id]['deleted'] = false

                # Its added now, so doesnt need to be found
                $log.log(self.foundNodes)
                delete self.foundNodes[results.data.mac]
                console.log('      - data', self.nodes)

                # Reset the button to search for more nodes now
                if Object.keys(self.foundNodes).length == 0
                    self.findingNodes = false
                self.submitButtonText = submitButtonTexts[self.findingNodes]
            ).catch(errFunc)

        this.findNodes = () ->
            $log.log('Searching for new nodes')

            self.findingNodes = true
            self.submitButtonText = submitButtonTexts[self.findingNodes]

            $http.post('/nodes/find').then((results) ->
                $log.log(' - id', results.data)

                if results.status == 200
                    $log.log("   - success: ", results.data)
                    for mac, item of results.data
                        self.foundNodes[mac] = results.data[mac]
                    console.log('     - data', self.foundNodes)

                    console.log('hey theyrer', Object.keys(self.foundNodes).length)
                    if Object.keys(self.foundNodes).length == 0
                        self.findingNodes = false
                    self.submitButtonText = submitButtonTexts[self.findingNodes]
                else
                    $log.log("   - failed:", results)
            ).catch(() ->
                self.findingNodes = false
                self.submitButtonText = submitButtonTexts[self.findingNodes]
            )

        @delete = (node) ->
            $log.log("Toggling the node! #{node.id}")

            $http.delete("/nodes/#{node.id}").then((results) ->
                $log.log(' - deleted successfully', results.data)

                delete self.nodes[results.data.result]
                node.deleted = true

                $log.log(' - new rules, ', self.nodes)
            ).catch(errFunc)

        return
    ]
)
