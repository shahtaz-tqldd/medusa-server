# medusa backend server
This is a medusa backend server developed with python and django with django rest framework. The sole purpose of this backend to use this as a authentication service, serve projects, blogs and skills. Also interact with a chatbot


## run on local environment
1. create a virtual environment
`python -m venv env`

2. activate virtual environment
`cd env\Scripts\activate` for windows
`source env/bin/activate` for linux

3. apply mirgations
`python manage.py migrate`

4. create/update the .env with database and other info

5. start the server
`python manage.py runserver`



## run with docker
1. create/update the .env with database and other info

2. run the docker
`bash start_app.sh` for linux, make sure you have docker installed in your local machine
`cd start_app.bat` for windows, make sure you have docker desktop running


** migrations cleanup command **
find . -path "*/migrations/*.pyc"  -delete
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
