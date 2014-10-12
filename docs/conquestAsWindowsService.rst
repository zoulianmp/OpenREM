Running Conquest on Windows as a service
****************************************

..  Note::  Content contributed by DJ Platten, with edit by ET McDonagh

This guide assumes Conquest has already been installed and runs ok. These
instructions are based on Windows XP.

Run as a service
----------------

#. Make sure conquest isn't running.
#. Open a file browser and navigate to your conquest folder.
#. Right-hand click on the "ConquestDICOMServer.exe" file and choose "Run as..."
#. Enter the username and password of a Windows user with administrator rights.
#. Once conquest is running, click on the "Install server as NT service" on the "Configuration" tab.
#. Close the conquest Window.
#. Log in to Windows as a user with administrator rights.
#. Go to "Control panel" -> "Administrative Tools" -> "Services".
#. There will be a service with the same name as conquest's AE title. Right-hand click the mouse on this service and select "Properties".
#. On the "Log On" tab check the box that says "Allow service to interact with the desktop".
#. Click "Apply" then "OK".
#. Right-hand click on the service again and click "Restart".

The "Allow service to interact with the desktop" seems to be necessary for the batch to run that puts the dose report into OpenREM.

Firewall settings
-----------------

Windows is able to change its firewall settings after you think everything is
working ok! Assuming you have control of the firewall, add three port exceptions 
to the Windows firewall on the server computer: ports 80 and 443 for Apache,
and whichever port that was chosen for conquest (104 is *the* port allocated
to DICOM, but you may have used a higher port above 1024 for permissions reasons).

The firewall instructions at `portforward.com <http://portforward.com/english/routers/firewalling/Microsoft/WindowsXPFirewallFirewall/Apache.htm>`_
were found to be a useful guide for this.
