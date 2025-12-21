def fetch_network_shape(city: str):
    pass

def fetch_network_metadata(city: str):
    pass


### TODO: validate incoming data with decorators maybe could be cool
# def _validate(meta_data_schema: Type[ComponentMetaData]):
#     def validated(func):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             meta_data_schema.model_validate(**kwargs)
#             return func(*args, **kwargs)
#         return wrapper
#     return validated