import os


# Dependent Services
BLUEPRINT_PARSER_URL = os.environ.get('BLUEPRINT_PARSER_URL', 'https://api.apiblueprint.org/parser')

# JSON Web Token
JWT_ALGORITHM = 'HS256'
JWT_KEY = os.environ.get('JWT_KEY')

# BrowserID
AUDIENCE = os.environ.get('AUDIENCE', 'https://bluepaste.herokuapp.com')

