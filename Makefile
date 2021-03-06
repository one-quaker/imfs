RUN=python manage.py

run: collectstatic
	$(RUN) runserver 0.0.0.0:8000

clean:
	rm -rfv *~*
	find . -name '*.pyc' -exec rm -fv {} \;

shell:
	$(RUN) shell_plus

makemigrations:
	$(RUN) makemigrations

showmigrations:
	$(RUN) showmigrations

migrate: clean
	$(RUN) migrate

collectstatic:
	$(RUN) collectstatic --noinput

create_admin:
	echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'pass')" | $(RUN) shell

pip_req:
	pip install -r requirements.txt

module_update:
	wget https://raw.githubusercontent.com/VyacheslavKorotach/Immutable_File_System/master/eos_imfs.py -O imfs_io/eos_imfs.py

service_restart:
	sudo systemctl restart web_ui && sudo systemctl restart lightdm
