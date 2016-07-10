def get_request_params(request_params):
    return {param['key']: param['value'] for param in request_params}
