Welcome to OpenREM's documentation!
===================================

.. image:: openrem0105.png
    :width: 105px
    :align: left
    :height: 105px
    :alt: OpenREM logo

OpenREM is an opensource framework created for the purpose of radiation 
exposure monitoring. The software is capable of importing and displaying 
data from a wide variety of x-ray dose related sources, and then enables 
easy export of the data in a form that is suitable for further analysis 
by suitably qualified medical physics personnel.

Please see `openrem.org <http://openrem.org>`_ for more details.


Contents:

..  toctree::
    :maxdepth: 2

    install
    releasenotes
    import
    interface
    code

..  Note::
    OpenREM does not currently include a DICOM Store SCP, ie you will
    need to install a DICOM store server in order to send RSDRs or other
    DICOM files from modalities.
    
    If you have no preference, `Conquest <http://ingenium.home.xs4all.nl/dicom.html>`_
    is recommended as a free, open source, scriptable DICOM server. Please
    note though that you will need to include the RSRD SOP in the dgatesop.lst
    file.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

