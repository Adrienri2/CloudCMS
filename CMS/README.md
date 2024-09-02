CloudCMS

pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate

python manage.py createsuperuser

python manage.py runserver


http://localhost:8000/swagger/



cd docs
make html

python manage.py test