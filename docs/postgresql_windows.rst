Installing PostgreSQL for OpenREM on Windows
*************************************************

..  Note:: Author JA Cole

Get PostgreSQL and the python connector
===========================================
    
+ Download the installer from http://www.enterprisedb.com/products-services-training/pgdownload#windows
+ Download psycopg2 from http://www.lfd.uci.edu/~gohlke/pythonlibs/. Make sure it matches your python and Windows version.

Install PostgreSQL
==================

Run the the postgresql installer. It will ask for a location. Ensure the "data" directory is *not* under "Program Files" as this can cause permissions errors.
Enter a superuser password when prompted. Make sure you keep this safe as you will need it.

Create a user and database
==============================

Open pgAdmin III

+ Click on servers to expand
+ Double click on PostgreSQL 9.3
+ Enter your superuser password
+ Right click on "login roles" and choose "New login role"
+ Create the openremuser (or whatever you want your user to be called) and under definition add a password.
+ Click OK
+ Right click on databases and choose "New database"
+ Name the database (openremdb is fine) and assign the the owner to the user you just created.


Install psycopg2
================
Run the installer you downloaded for psycopg2 earlier.


Configure OpenREM to use the database
=====================================

Find and edit the settings file (notepad works fine). The path depends on your python install, but could be something like:
    + ``C:\lib\python2.7\site-packages\openrem\openrem\settings.py``

Set the following (changing name, user and password as appropriate):
    + ``'ENGINE': 'django.db.backends.postgresql_psycopg2',``
    + ``'NAME': 'openrem_db',``
    + ``'USER': 'openremuser',``
    + ``'PASSWORD': 'openrem_pw',``

Fire it up with OpenREM
=======================

+ ``python path/to/openrem/manage.py syncdb``
+ ``python path/to/openrem/manage.py convert_to_south remapp``

Fix '' value too long for type character varying(50)'' error
============================================================

This error is caused by the django auth_permissions system not being able to cope with long names in the models.

+ Open pgAdmin III
+ Open Servers
+ Open databases
+ Open the openrem database
+ Open schemas
+ Open public
+ Open tables
+ right click on auth_permission
+ Select properties
+ Change ''name'' to ''varying(100)'' from ''varying(50)''

Then run ``python path/to/openrem/manage.py syncdb`` again.
