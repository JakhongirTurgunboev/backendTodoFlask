This is backend part of fullstack application written with
Flask, Flask-restful, SQLAlchemy in the backend.
React, Redux in the frontend.

All code is written inside one file called app.py
Because this is just demonstration it is done so.
But, in real life applications, it is advised to divide the
project to smaller manageable chunks.

Only admin with authorization can change the details in the view.
Update the todo and delete it.

Registering new user is not implemented yet, you can login with
username:admin and password:123

Run ```flask run``` command on localhost and
``gunicorn app:app`` when running on server
