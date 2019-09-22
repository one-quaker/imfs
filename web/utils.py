def random_string(size=5):
    import string
    import random

    string_tpl = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(string_tpl) for i in range(size))


def path_and_rename(instance, file_obj):
    import os

    upload_to = 'photo'
    fext = file_obj.split('.')[-1].lower()
    random_fn = random_string()
    if instance.pk:
        file_obj = '{}.{}'.format(instance.pk, fext)
    else:
        file_obj = '{}.{}'.format(random_fn, fext)
    return os.path.join(upload_to, file_obj)


def rm_dir(dp):
    import os
    import shutil

    if os.path.isdir(dp):
        print(f'Removing directory "{dp}"')
        shutil.rmtree(dp)


def mk_dir(dp):
    import os

    if not os.path.isdir(dp):
        print(f'Creating directory "{dp}"')
        os.mkdir(dp)


def rm_file(fp):
    import os

    if os.path.isfile(fp):
        print(f'Removing file "{fp}"')
        os.remove(fp)
