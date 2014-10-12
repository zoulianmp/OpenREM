OpenREM Release Notes version 0.4.3
***********************************

Headline changes
================


* Export of study information is now handled by a task queue - no more export time-outs.
* Patient size information in csv files can now be uploaded and imported via a web interface.
* Proprietary projection image object created by Hologic tomography units can now be interrogated for details of the tomosynthesis exam.
* Settings.py now ships with its proper name, this will overwrite important local settings if upgrade is from 0.3.9 or earlier.
* Time since last study is no longer wrong just because of daylight saving time!
* Django release set to 1.6; OpenREM isn't ready for Django 1.7 yet
* The inner ``openrem`` Django project folder is now called ``openremproject`` to avoid import conflicts with Celery on Windows
* DEBUG mode now defaults to False

Specific upgrade instructions
=============================

**Always make sure you have converted your database to South before attempting an upgrade**

Quick reminder of how, if you haven't done it already:

    Linux::

        python /usr/local/lib/python2.7/dist-packages/openrem/manage.py convert_to_south remapp

    Windows::

        python C:\Python27\Lib\site-packages\openrem\manage.py convert_to_south remapp

Upgrading from 0.3.9 or earlier
-------------------------------

**It is essential that you upgrade to at least 0.4.0 first**, then upgrade to
0.4.3. Otherwise the settings file will be overwritten and you will lose
your database settings. There is also a trickier than usual database
migration and instructions for setting up users. *Fresh installs should start
with the latest version.*

Upgrade to version 0.4.2

.. sourcecode:: bash

    pip install openrem==0.4.2

(Will need ``sudo`` or equivalent if using linux without a virtualenv)

Then follow the instructions in :doc:`release-0.4.0` from migrating the
database onwards, before coming back to these instructions.


Upgrading from 0.4.0 or above
-----------------------------

Install OpenREM version 0.4.3
`````````````````````````````
.. sourcecode:: bash

    pip install openrem==0.4.3

(Will need ``sudo`` or equivalent if using linux without a virtualenv)

RabbitMQ
````````

The message broker RabbitMQ needs to be installed to enable the export and upload features

* Linux - Follow the guide at http://www.rabbitmq.com/install-debian.html
* Windows - Follow the guide at http://www.rabbitmq.com/install-windows.html

Move and edit local_settings.py file and wsgi.py files
``````````````````````````````````````````````````````
The inner ``openrem`` Django project folder has now been renamed ``openremproject``
to avoid import confusion that prevented Celery working on Windows.

When you upgrade, the ``local_settings.py`` file and the ``wsgi.py`` file will
remain in the old ``openrem`` folder. Both need to be moved across to the
``openremproject`` folder, and edited as below.

The new and old folders will be found in:

* Linux: ``/usr/local/lib/python2.7/dist-packages/openrem/``
* Linux with virtualenv: ``/home/myname/openrem/lib/python2.7/site-packages/openrem/``
* Windows: ``C:\Python27\Lib\site-packages\openrem\``


Edit the local_settings.py file
```````````````````````````````

The ``MEDIA_ROOT`` path needs to be defined. This is
the place where the study exports will be stored for download and where the
patient size information csv files will be stored temporarily whilst they
are bing processed.

The path set for ``MEDIA_ROOT`` is up to you, but the user that runs the
webserver must have read/write access to the location specified because
it is the webserver than reads and writes the files. In a debian linux,
this is likely to be ``www-data`` for a production install. Remember to use
forward slashes in the config file, even for Windows.

Linux example::

    MEDIA_ROOT = "/var/openrem/media/"

Windows example::

    MEDIA_ROOT = "C:/Users/myusername/Documents/OpenREM/media/"

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

Edit the wsgi.py file with the new project folder name
``````````````````````````````````````````````````````
If you aren't using the wsgi.py file as part of your webserver setup,
you might like to simply rename the ``wsgi.py.example`` file in the
``openremproject`` folder.

If you are using it, edit the line::

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "openrem.settings")

to read::

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "openremproject.settings")

Tidying up
``````````
Finally, you should delete the old ``openrem`` folder - you might like to
take a backup first!

Database migration
``````````````````
*Assuming no virtualenv*

Linux::

    python /usr/local/lib/python2.7/dist-packages/openrem/manage.py schemamigration --auto remapp
    python /usr/local/lib/python2.7/dist-packages/openrem/manage.py migrate remapp

Windows::

    C:\Python27\Lib\site-packages\openrem\manage.py schemamigration --auto remapp
    C:\Python27\Lib\site-packages\openrem\manage.py migrate remapp

Web server
``````````

If you are using a production webserver, you will probably need to edit
some of the configuration to reflect the change in location of ``settings.py``,
for example ``DJANGO_SETTINGS_MODULE = openremproject.settings``, and then
restart the web server. You may need to do something similar for the location
of ``wsgi.py``.

If you are using the built-in test web server (`not for production use`),
then the static files will not be served unless you add ``--insecure``
to the command. This is one of the consequences of setting ``DEBUG`` to
``False``::

    python manage.py runserver x.x.x.x:8000 --insecure


Start the Celery task queue
```````````````````````````
..  Note::

    The webserver and Celery both need to be able to read and write to the
    ``MEDIA_ROOT`` location. Therefore you might wish to consider starting
    Celery using the same user or group as the webserver, and setting the
    file permissions accordingly.

For testing, in a new shell: *(assuming no virtualenv)*

Linux::

    cd /usr/local/lib/python2.7/dist-packages/openrem/
    celery -A openremproject worker -l info

Windows::

    cd C:\Python27\Lib\site-packages\openrem\
    celery -A openremproject worker -l info

For production use, see http://celery.readthedocs.org/en/latest/tutorials/daemonizing.html

