Export from database
====================
    
Multi-sheet Microsoft Excel XLSX exports
++++++++++++++++++++++++++++++++++++++++
This export has a summary sheet of all the requested and performed 
protocols and the series protocols. The next sheet has all studies on,
one study per line, with the series stretching off to the right. The
remaining sheets are specific to each series protocol, in alphabetical
order, with one series per line. If one study has three series with the
same protocol name, each one has a line of its own.

.. autotask:: remapp.exports.xlsx.ctxlsx


Single sheet CSV exports
++++++++++++++++++++++++
   
.. autotask:: remapp.exports.exportcsv.exportFL2excel
.. autotask:: remapp.exports.exportcsv.exportCT2excel
.. autotask:: remapp.exports.exportcsv.exportMG2excel

Specialised csv exports - NHSBSP formatted mammography export
-------------------------------------------------------------

.. autotask:: remapp.exports.mg_csv_nhsbsp.mg_csv_nhsbsp
