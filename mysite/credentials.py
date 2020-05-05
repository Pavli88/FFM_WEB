
class Credentials:

    def __init__(self):
        self.db_parameters = {
            'default': {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': 'ffm_web',
                'USER': 'root',
                'PASSWORD': 'test88',
                'HOST': 'localhost',
                'PORT': '3306',
            }
        }