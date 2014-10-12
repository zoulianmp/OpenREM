Installing PostgreSQL for OpenREM on Ubuntu linux
*************************************************

Install PostgreSQL and the python connector
===========================================
    
+ ``sudo apt-get install postgresql``
+ ``sudo apt-get build-dep python-psycopg2``

The second command installed a lot of things, at least some of which are
necessary for this to work!

If you are using a virtualenv, make sure you are in it and it is active (``source bin/activate``)

+ ``pip install psycopg2``

Create a user for the database
==============================

+ ``sudo passwd postgres``
+ Enter password, twice
+ ``sudo -u postgres createuser -P openrem_user``
+ Enter password, twice
+ Superuser, *No*
+ Create databases, *No*
+ Create new roles, *No*

Optional: Specify the location for the database
-----------------------------------------------

You might like to do this if you want to put the database on an encrypted
location

For this example, I'm going to assume all the OpenREM programs and data are in the folder ``/var/openrem/``:

    + ``sudo /etc/init.d/postgresql stop``
    + ``mkdir /var/openrem/database``
    + ``sudo cp -aRv /var/lib/postgresql/9.1/main /var/openrem/database/`` 
    + ``sudo nano /etc/postgresql/9.1/main/postgresql.conf``

    Change the line 
        + ``data_directory = '/var/lib/postgresql/9.1/main'`` to
        + ``data_directory = '/var/openrem/database/main'``

    + ``sudo /etc/init.d/postgresql start``

Create the database
===================

+ ``su postgres``
+ ``psql template1``
+ ``CREATE DATABASE openrem_db OWNER openrem_user ENCODING 'UTF8';``
+ ``\q``
+ ``exit``

Change the security configuration
=================================

The default security settings are too restrictive to allow access to the database.

+ ``sudo nano /etc/postgresql/9.1/main/pg_hba.conf``
+ Add the following line:
    + ``local openrem_db openrem_user md5``
+ ``sudo /etc/init.d/postgresql restart``

Configure OpenREM to use the database
=====================================

Find and edit the settings file, eg
    + ``nano local/lib/python2.7/site-packages/openrem/openrem/settings.py``

Set the following (changing name, user and password as appropriate):
    + ``'ENGINE': 'django.db.backends.postgresql_psycopg2',``
    + ``'NAME': 'openrem_db',``
    + ``'USER': 'openremuser',``
    + ``'PASSWORD': 'openrem_pw',``

Fire it up with OpenREM
=======================

+ ``python path/to/openrem/manage.py syncdb``
+ ``python path/to/openrem/manage.py convert_to_south remapp``



