``genno``: efficient, transparent calculation on N-D data
*********************************************************

**genno** is a Python package for describing and executing complex calculations on labelled, multi-dimensional data.
It aims to make these calculations efficient, transparent, and easily validated as part of scientific research.

genno is built on high-quality Python data packages including :py:`dask`, :mod:`xarray`, and ```pint``; and provides (current or planned) compatibility with packages including :mod:`pandas`, :mod:`matplotlib`, :mod:`plotnine <.compat.plotnine>`, :mod:`ixmp`, :mod:`sdmx1 <.compat.sdmx>`, and :mod:`pyam <.compat.pyam>`.

.. toctree::
   :maxdepth: 2
   :caption: User guide

   usage
   config
   cache
   api

.. _compat:

Compatibility
=============

:mod:`.genno` provides built-in support for interaction with:

- :doc:`Plotnine <compat-plotnine>` (:mod:`plotnine`), via :mod:`.compat.plotnine`.
- :doc:`Pyam <compat-pyam>` (:mod:`pyam`), via :mod:`.compat.pyam`.
- :doc:`SDMX <compat-sdmx>` (:mod:`sdmx`), via :mod:`.compat.sdmx`.

.. toctree::
   :maxdepth: 1
   :caption: Compatibility
   :hidden:

   compat-plotnine
   compat-pyam
   compat-sdmx

Packages that extend :mod:`genno` include:

- :mod:`ixmp.report`
- :mod:`message_ix.report`

.. toctree::
   :maxdepth: 2
   :caption: Development

   whatsnew
   releasing

License
=======

Copyright © 2018–2024 genno contributors.

Licensed under the GNU General Public License, version 3.0.


Name
====

A 玄能 (*genno* or *gennoh*) is a type of hammer used in Japanese woodworking.
The package name is warning, by reference, to the adage “When you hold a hammer, every problem looks like a nail”: you shouldn't hit everything with ``genno``, but it is still a useful and versatile tool.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
