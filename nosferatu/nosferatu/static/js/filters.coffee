angular.module('nosferatuApp') .filter('notthesame', () ->
    return (input, rselect) ->
        if not input?
            return input
        if not rselect?
            return input
        result = []
        angular.forEach(input, (value) ->
            if value.name? and value.name isnt rselect.node.name
                result.push(value)
        )
        return result
)
