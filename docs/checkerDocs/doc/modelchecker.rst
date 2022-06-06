Model checker
==============

Construction history
---------------------

( **code**: *checker.model.deleteHistory_check* )

* Check: Verifies that the geometries in the scene do not contain history.
* Sel: Select all geometries with construction history.
* Fix: Delete construction history for all geometries nodes.

.. figure:: /images/constructionHistory.gif
   :align: center
   :scale: 100 %

   *Construction history.*


Reset transform
----------------

* Check: Verifies if all pivots are at the origin.
* Fix: Center all transform nodes pivots to the origin.
* Sel: Select all transform nodes do not have the pivot at the origin.

.. figure:: /images/resetTransform.gif
   :align: center
   :scale: 100 %

   *Pivot example.*


Freeze transform
-----------------


* Check: Use to detect all transforms nodes with no *zero transfroms*.  ( translate 0,0,0 rotate 0,0,0 scale 1,1,1)
* Fix: Freeze object transforms.
* Sel: Select all transfroms nodes with not *zero-trnasforms*.


Symmetry
---------

.. figure:: /images/sym.gif
   :align: center
   :scale: 100 %

   *Symmetry check.*

Check worldspace symmetry on selection mesh based on X axis, if no mesh are selected the checker takes all mesh who are intersect on world X axis.
indicating with a warning that objects are not symmetrical.

.. note:: Depends on the amount to vertex the check **may take long..**. (*be patient* )  

* Check: Check for symmetry.
* Sel: Select all non symmetry geometries along X axis.

