#!/usr/bin/env bash

source /app_conf/services/scripts.sh

run_python_script "Coletando arquivos estáticos" "manage.py collectstatic --noinput --verbosity 0"
run_python_script_with_output "Atualizando Site ID" "manage.py loaddata 000_site"
run_python_script_with_output "Making migrations" "manage.py makemigrations"
run_python_script_with_output "Migrating" "manage.py migrate"

echo " > Iniciando SERVER"
echo ;
echo "########################################################################"
echo ;
source /app_conf/services/uwsgi-env.sh
uwsgi --enable-threads --cache 5000 --thunder-lock --show-config --static-map /static-policy/=/code/static/ --static-map /media-policy/=/code/media/
