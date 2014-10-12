OpenREM Release Notes version 0.4.0
***********************************

Headline changes
================================
* User authentication has been added
* Studies can be deleted from the web interface
* Import scripts can now be passed a list of files, eg ``python openrem_rdsr.py *.dcm``
* Date of birth no longer retained for mammography (bug fix - correct behaviour already existed for other imports)
* General bug fixes to enable import from wider range of sources
* Improved user documentation

Specific upgrade instructions
=============================

*  ``pip install openrem==0.4.2`` `Go straight to 0.4.2`
*  Migrate the database

    ..      Warning::
        
            A database migration is required that will need a choice to be made

    * Linux: ``python /usr/lib/python2.7/dist-packages/openrem/manage.py schemamigration --auto remapp``
    * Windows: ``C:\Python27\Lib\site-packages\openrem\manage.py schemamigration --auto remapp``

    When South has considered the changes to the schema, you will see the following message::
    
     ? The field 'Observer_context.device_observer_name' does not have a default specified, yet is NOT NULL.
     ? Since you are making this field nullable, you MUST specify a default
     ? value to use for existing rows. Would you like to:
     ?  1. Quit now.
     ?  2. Specify a one-off value to use for existing columns now
     ?  3. Disable the backwards migration by raising an exception; you can edit the migration to fix it later
     ? Please select a choice: 3

    As per the final line above, the correct choice is ``3``. The fields that are now
    nullable previously weren't. Existing data in those fields will have a value, or those
    tables don't exist in the current database. The problem scenario is if after
    the migration these tables are used and one of the new nullable fields is left as null,
    you will not be able to migrate back to the old database schema without error.
    This is not something that you will want to do, so this is ok.

    Do the migration:
    
    * Linux: ``python /usr/lib/python2.7/dist-packages/openrem/manage.py migrate remapp``
    * Windows: ``C:\Python27\Lib\site-packages\openrem\manage.py migrate remapp``    

*  Update the settings files

    ..      Warning::

            The settings file has changed and will need to be manually edited.

    Changes need to be made to the ``settings.py`` file where the database details are stored.
    Normally upgrades don't touch this file and the copy in the upgrade has a ``.example`` suffix.
    **This upgrade and potentially future ones will need to change this file**, so the 
    format has been changed. The ``settings.py`` file will now be replaced
    each time the code is upgraded. In addition, there is a new ``local_settings.py``
    file that contains things that are specific to your installation, such as the
    database settings.

    This upgrade will include a file called ``settings.py.new`` and the ``local_settings.py.example``
    file. You will need to do the following:

    *   Copy the database settings from your current ``settings.py`` file to the ``local_settings.py.example`` file
        and rename it to remove the ``.example``. 
        Both of these files are in the ``openrem/openrem`` directory, which will be somewhere like 
        
        *   Linux: ``/usr/lib/python2.7/dist-packages/openrem/openrem/``
        *   Windows: ``C:\Python27\Lib\site-packages\openrem\openrem\``

    *   Move the existing ``settings.py`` out of the python directories
    *   Rename the ``settings.py.new`` to ``settings.py``

* Create a new secret key

    All versions of openrem ship with the same secret key. This key is used for web security
    checks, and should be unique (and secret) for each installation.
    
    *   Generate a new secret key - http://www.miniwebtool.com/django-secret-key-generator/ is a 
        suitable method of creating a new key.
    *   Copy the new key and use it to replace the default key in the ``local_settings.py`` file

* Restart your webserver

* Add some users

    * Go to the admin interface (eg http://localhost:8000/admin) and log in with the user created when you originally created the database (``manage.py syncdb``)
    * Create some users and add them to the appropriate groups (if there are no groups, go to the OpenREM homepage and they should be created).

        + ``viewgroup`` can browse the data only
        + ``exportgroup`` can do as view group plus export data to a spreadsheet, and will be able to import height and weight data in due course (See `Issue #21 <https://bitbucket.org/openrem/openrem/issue/21/>`_)
        + ``admingroup`` can delete studies in addition to anything the export group can do


