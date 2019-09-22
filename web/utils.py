def random_string(size=6):
    import string
    import random

    string_tpl = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(string_tpl) for i in range(size))


def path_and_rename(instance, file_obj):
    import os

    upload_to = 'photo'
    fext = file_obj.split('.')[-1]
    random_fn = random_string(4)
    if instance.pk:
        file_obj = '{}.{}'.format(instance.pk, fext)
    else:
        file_obj = '{}.{}'.format(random_fn, fext)
    return os.path.join(upload_to, file_obj)
