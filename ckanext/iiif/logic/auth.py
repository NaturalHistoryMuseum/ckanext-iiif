from ckantools.decorators import auth


@auth(anon=True)
def build_iiif_resource(context, data_dict):
    """
    Auth for building a IIIF resource, always allowed.

    :param context:
    :param data_dict:
    """
    return {'success': True}


@auth(anon=True)
def build_iiif_identifier(context, data_dict):
    """
    Auth for building a IIIF identifier, always allowed.

    :param context:
    :param data_dict:
    """
    return {'success': True}
