## Basic Chat Backend
The Backend is build with django-restframework and completely based on the model/view and serializer logic provided by django.
Communication with a potential frontend is based on REST, realtime features could be added using websockets.
This is really basic but search and filter options could easily be added.

### How to run it ?

#### Install packages
```
pip install -r requirements.txt
```
#### Setup database
```
py manage.py makemigrations
py manage.py migrate
py manage.py populate_db 
```
#### Run Tests
```
py manage.py tests
```
#### Run Development Server
```
py manage.py runserver
```
