Backing up MySQL on Windows
===========================

..  Note::  Content contributed by DJ Platten

These instructions are based on Windows XP.


As a one-off, create a MySQL user called ``backup`` with a password of ``backup`` that has full rights to the database:

..  code-block:: mysql

    C:\Program Files\MySQL\MySQL Server 5.6\bin\mysql.exe -u root -p -e "CREATE USER 'backup'@'localhost' IDENTIFIED BY 'backup'";

Grant the ``backup`` user full privileges on the database called ``openremdatabasemysql``:

..  code-block:: mysql

    C:\Program Files\MySQL\MySQL Server 5.6\bin\mysql.exe -u root -p -e "GRANT ALL PRIVILEGES ON openremdatabasemysql .* TO 'backup'@'localhost'";

Grant the ``backup`` user privileges to create databases:

..  code-block:: mysql

    C:\Program Files\MySQL\MySQL Server 5.6\bin\mysql.exe -u root -p -e "GRANT CREATE ON *.* TO 'backup'@'localhost'";

Reload the privileges to ensure that MySQL registers the new ones:

..  code-block:: mysql

    C:\Program Files\MySQL\MySQL Server 5.6\bin\mysql.exe -u root -p -e "FLUSH PRIVILEGES";


To backup the contents of the database from the command line to a file called ``backup.sql`` (note that the lack of spaces after the ``-u`` and ``-p`` is not a typo):

..  code-block:: posh

    C:\Program Files\MySQL\MySQL Server 5.6\bin\mysqldump.exe -ubackup -pbackup openremdatabasemysql > backup.sql

To restore the database, assuming that it doesn't exist anymore, first it needs to be created:

..  code-block:: posh

    C:\Program Files\MySQL\MySQL Server 5.6\bin\mysql.exe -ubackup -pbackup -e "CREATE DATABASE openremdatabasemysql";

Then restore the contents of the database from a file called ``backup.sql``:

..  code-block:: posh

    C:\Program Files\MySQL\MySQL Server 5.6\bin\mysql.exe -ubackup -pbackup openremdatabasemysql < backup.sql



An example DOS batch file to back up the contents of the ``openremdatabasemysql`` database using a time stamp of the form ``yyyy-mm-dd_hhmm``, zip up the resulting file, delete the uncompressed version and then copy it to a network location (the network copy will only work if the user that runs the batch file has permission on the
network):

..  code-block:: bash

    @echo off
    For /f "tokens=1-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%b-%%a)
    For /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)

    "C:\Program Files\MySQL\MySQL Server 5.6\bin\mysqldump.exe" -ubackup -pbackup openremdatabasemysql > F:\OpenREMdatabase\backup\%mydate%_%mytime%_openremdatabasemysql.sql

    "C:\Program Files\7-Zip\7z.exe" a F:\OpenREMdatabase\backup\%mydate%_%mytime%_openremdatabasemysql.zip F:\OpenREMdatabase\backup\%mydate%_%mytime%_openremdatabasemysql.sql

    del F:\OpenREMdatabase\backup\%mydate%_%mytime%_openremdatabasemysql.sql

    copy F:\OpenREMdatabase\backup\%mydate%_%mytime%_openremdatabasemysql.zip "\\Srv-mps-001\xls_protect\PATDOSE\OpenREMbackup\"
