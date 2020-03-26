from ckan.plugins import interfaces


class IIIIF(interfaces.Interface):
    '''
    This (horribly named) interface allows other plugins to hook into the IIIF plugin.
    '''

    def get_builders(self):
        '''
        :return: a list of classes with regex and get_builder properties
        '''
        pass
