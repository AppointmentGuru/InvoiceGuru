
class MultiSerializerMixin():
    '''
    A mixins that allows you to easily specify different serializers for various verbs
    '''

    def get_serializer_class(self):
        print(self.action)
        default_serializer = self.default_serializer_class
        return self.serializer_map.get(self.action, default_serializer)
