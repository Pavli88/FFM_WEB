def dynamic_mode_get(request_object, column_list, table):
    filters = {}
    for key, value in request_object:
        if value == '':
            pass
        else:
            if key in column_list:
                filters[key] = value
    return list(table.objects.filter(**filters).values())


def dynamic_model_create(table_object, request_object):
    object_data = table_object
    for key, value in request_object.items():
        setattr(object_data, key, value)
    object_data.save()
    return object_data


def dynamic_model_update(table_object, request_object):
    object_data = table_object.objects.get(id=request_object['id'])
    for key, value in request_object.items():
        setattr(object_data, key, value)
    object_data.save()
    return object_data