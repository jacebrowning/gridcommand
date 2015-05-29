"""Parses requests coming into routes."""

# from flask_api import status, exceptions
# from webargs import core
# from webargs.flaskparser import FlaskParser
#
#
# parser = FlaskParser(('query', 'form', 'json', 'data'))
#
#
# @parser.location_handler('data')
# def parse_data(req, name, arg):
#     data = req.data
#     if data:
#         return core.get_value(data, name, arg.multiple)
#     else:
#         return core.Missing
#
#
# @parser.error_handler
# def handle_error(error):
#     if error.status_code == status.HTTP_400_BAD_REQUEST:
#         message = str(error).replace('"', "'")
#         raise exceptions.ParseError(message)
#     else:
#         raise error
