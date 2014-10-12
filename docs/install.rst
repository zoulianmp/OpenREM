Installation instructions
*************************

OpenREM can be installed with a single command; however, there are two
prerequisites that need to be installed first – python and pip – and
RabbitMQ needs to be installed for exports and patient size imports to work.

Once installed, there are a few configuration choices that need to be made,
and finally a couple of services that need to be started. Then you are
ready to go!

Install the prerequisites
=========================

Install Python 2.7.x
--------------------

* Linux – likely to be installed already
* Windows – https://www.python.org/downloads

Add Python and the scripts folder to the path
`````````````````````````````````````````````
*Windows only – this is usually automatic in linux*

Add the following to the end of the ``path`` environment variable (to see
how to edit the environment variables, see http://www.computerhope.com/issues/ch000549.htm)::

    ;C:\Python27\;C:\Python27\Scripts\

Setuptools and pip
------------------

Install setuptools and pip – for details go to
http://www.pip-installer.org/en/latest/installing.html. The quick version
is as follows:

Linux

    Download the latest version using the same method as for Windows, or
    get the version in your package manager, for example::

        sudo apt-get install python-pip

Windows

    Download the installer script `get-pip.py <https://bootstrap.pypa.io/get-pip.py>`_
    and save it locally – right click and *Save link as...* or equivalent.

    Open a command window (Start menu, cmd.exe) and navigate to the place
    you saved the get‑pip.py file::

        python get-pip.py



Quick check of python and pip
`````````````````````````````

To check everything is installed correctly so far, type the following in a 
command window/shell. You should have the version number of pip returned to 
you::

    pip -V

Install RabbitMQ
----------------
*(New for version 0.4.3)*

* Linux - Follow the guide at http://www.rabbitmq.com/install-debian.html
* Windows - Follow the guide at http://www.rabbitmq.com/install-windows.html

For either install, just follow the defaults – no special configurations required.

..  Note::

    Before continuing, `consider virtualenv`_

Install and configure OpenREM
=============================

Install
--------

.. sourcecode:: bash

    pip install openrem

*Will need ``sudo`` or equivalent if installing on linux without using a virtualenv*

Configure
---------

Locate install location

* Linux: ``/usr/local/lib/python2.7/dist-packages/openrem/`` or ``/usr/lib/python2.7/site-packages/openrem/``
* Windows: ``C:\Python27\Lib\site-packages\openrem\``

There are two files that need renaming:

+ ``openremproject/local_settings.py.example`` to ``openremproject/local_settings.py``
+ ``openremproject/wsgi.py.example`` to ``openremproject/wsgi.py``

In the ``local_settings.py`` file, set the database details, the ``MEDIA_ROOT`` path, the secret key and the ``ALLOWED_HOSTS``.

..  Note::

    Windows notepad will not recognise the Unix style line endings.
    Please use an editor such as Notepad++ or Notepad2 if you can, else use WordPad –
    on the View tab you may wish to set the Word wrap to 'No wrap'

Database settings
`````````````````

For testing you can use the SQLite3 database

.. sourcecode:: python

    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': '/ENTER/PATH/WHERE/DB/FILE/CAN/GO',

* Linux example: ``'NAME': '/home/user/openrem/openrem.db',``
* Windows example: ``'NAME': 'C:/Users/myusername/Documents/OpenREM/openrem.db',`` *Note use of forward slash in configuration files*

For production use, see `Database options`_ below

Location setting for imports and exports
`````````````````````````````````````````

Csv and xlsx study information exports and patient size csv imports are
written to disk at a location defined by ``MEDIA_ROOT``.

The path set for ``MEDIA_ROOT`` is up to you, but the user that runs the
webserver must have read/write access to the location specified because
it is the webserver than reads and writes the files. In a debian linux,
this is likely to be www-data for a production install. Remember to use
forward slashes for the config file, even for Windows.

Linux example::

    MEDIA_ROOT = "/var/openrem/media/"

Windows example::
    
    MEDIA_ROOT = "C:/Users/myusername/Documents/OpenREM/media/"


Secret key
``````````

Generate a new secret key and replace the one in the ``local_settings.py`` file. You can use
http://www.miniwebtool.com/django-secret-key-generator/ for this.

Allowed hosts
`````````````

The ``ALLOWED_HOSTS`` needs to be defined, as the ``DEBUG`` mode is now
set to ``False``. This needs to contain the server name or IP address that
will be used in the URL in the web browser. For example::

    ALLOWED_HOSTS = [
        '192.168.56.102',
        '.doseserver.',
        'localhost',
    ]

A dot before a hostname allows for subdomains (eg www.doseserver), a dot
after a hostname allows for FQDNs (eg doseserver.ad.trust.nhs.uk)

Create the database
-------------------

Linux::

    python /usr/local/lib/python2.7/dist-packages/openrem/manage.py syncdb

Windows::

    python C:\Python27\Lib\site-packages\openrem\manage.py syncdb

Answer each question as it is asked, do setup a superuser. This username and
password wil be used to log into the admin interface to create the usernames
for using the web interface. See the `Start using it!`_ section below.

Help! I get a ``value too long for type character varying(50)`` error!
    This error with part of the Django auth_permissions system that we are not using, and can safely be ignored.
    This is being tracked as `Issue 62 <https://bitbucket.org/openrem/openrem/issue/62>`_

For production installs, convert to South
`````````````````````````````````````````
`(What is south?)`_

Linux::

    python /usr/local/lib/python2.7/dist-packages/openrem/manage.py convert_to_south remapp

Windows::

    python C:\Python27\Lib\site-packages\openrem\manage.py convert_to_south remapp


Start all the services
======================

Start test web server
---------------------

Linux::

    python /usr/local/lib/python2.7/dist-packages/openrem/manage.py runserver --insecure

Windows::

    python C:\Python27\Lib\site-packages\openrem\manage.py runserver --insecure

If you are using a headless server and need to be able to see the 
web interface from another machine, use 
``python /usr/lib/python2.7/dist-packages/openrem/manage.py runserver x.x.x.x:8000 --insecure`` 
(or Windows equivalent) replacing the ``x`` with the IP address of the server 
and ``8000`` with the port you wish to use.

Open the web addesss given, appending ``/openrem`` (http://localhost:8000/openrem)

..  Note::

    Why are we using the ``--insecure`` option? With ``DEBUG`` mode set to ``True``
    the test web server would serve up the static files. In this release,
    ``DEBUG`` mode is set to ``False``, which prevents the test web server
    serving those files. The ``--insecure`` option allows them to be served again.

Start the Celery task queue
---------------------------
*(New for version 0.4.3)*

Celery will have been automatically installed with OpenREM, and along with
RabbitMQ allows for asynchronous task processing for imports and exports.

..  Note::

    The webserver and Celery both need to be able to read and write to the
    ``MEDIA_ROOT`` location. Therefore you might wish to consider starting
    Celery using the same user or group as the webserver, and setting the
    file permissions accordingly.

In a new shell:

Linux::

    cd /usr/local/lib/python2.7/dist-packages/openrem/
    celery -A openremproject worker -l info

Windows::

    cd C:\Python27\Lib\site-packages\openrem\
    celery -A openremproject worker -l info

For production use, see `Daemonising Celery`_ below

Start using it!
---------------

Add some data!

.. sourcecode:: bash

    openrem_rdsr.py rdsrfile.dcm

Add some users *(New in version 0.4.0)*

* Go to the admin interface (eg http://localhost:8000/admin) and log in with the user created when you created the database (``syncdb``)
* Create some users and add them to the appropriate groups (if there are no groups, go to the OpenREM homepage and they should be created).

    + ``viewgroup`` can browse the data only
    + ``exportgroup`` can do as view group plus export data to a spreadsheet
    + ``admingroup`` can delete studies and import height and weight data in addition to anything the export group can do

* Return to the OpenREM interface (eg http://localhost:8000/openrem) and log out of the superuser in the top right corner and log in again using one of the new users you have just created.

Further instructions
====================

Database options
----------------

SQLite is great for getting things running quickly and testing if the setup works,
but is really not recommended for production use on any scale. Therefore it is
recommended to use a different database such as `PostgreSQL <http://www.postgresql.org>`_ or 
`MySQL <http://www.mysql.com>`_.

Here are instructions for installing PostgreSQL on linux and on Windows:

..  toctree::
    :maxdepth: 1
    
    postgresql
    postgresql_windows

..  _convert-to-south:

Database migrations
-------------------

South is a django application to manage database migrations. Using
South means that future changes to the database model can be calculated
and executed automatically with simple commands when OpenREM is upgraded.

Production webservers
---------------------

Unlike the database, the production webserver can be left till later and
can be changed again at any time.

For performance it is recommended that a production webserver is used instead of the inbuilt 'runserver'.
Popular choices would be either `Apache <http://httpd.apache.org>`_ or you can do as the cool kids
do and use `Gunicorn with nginx <http://www.robgolding.com/blog/2011/11/12/django-in-production-part-1---the-stack/>`_.

The `django website <https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/modwsgi/>`_ 
has instructions and links to get you set up with Apache.

Daemonising Celery
------------------
*(New for version 0.4.3)*

In a production environment, Celery will need to start automatically and
not depend on a particular user being logged in. Therefore, much like
the webserver, it will need to be daemonised. For now, please refer to the
instructions and links at http://celery.readthedocs.org/en/latest/tutorials/daemonizing.html.

Virtualenv and virtualenvwrapper
--------------------------------

If the server is to be used for more than one python application, or you 
wish to be able to test different versions of OpenREM or do any development,
it is highly recommended that you use `virtualenv`_ or maybe `virtualenvwrapper`_

Virtualenv sets up an isolated python environment and is relatively easy to use.

If you do use virtualenv, all the paths referred to in the documentation will
be changed to:

* Linux: ``lib/python2.7/site-packages/openrem/``
* Windows: ``Lib\site-packages\openrem``

In Windows, even when the virtualenv is activated you will need to call `python`
and provide the full path to script in the `Scripts` folder. If you call the
script (such as `openrem_rdsr.py`) without prefixing it with `python`, the
system wide Python will be used instead. This doesn't apply to Linux, where
once activated, the scripts can be called without a `python` prefix from anywhere. 


Related guides
==============

    ..  toctree::
        :maxdepth: 1
        
        conquestAsWindowsService
        backupMySQLWindows

Advanced guides for developers
------------------------------

    ..  toctree::
        :maxdepth: 1
        
        apache_on_windows


.. _virtualenv: https://pypi.python.org/pypi/virtualenv
.. _virtualenvwrapper: http://virtualenvwrapper.readthedocs.org/en/latest/
.. _(What is south?): `Database migrations`_
.. _consider virtualenv: `Virtualenv and virtualenvwrapper`_
