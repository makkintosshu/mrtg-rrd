mrtg-rrd
========
by Jan "Yenya" Kasprzak <kas@fi.muni.cz> & Morgan Aldridge <morgant@makkintosshu.com>

OVERVIEW
--------

This is a fork of Jan "Yenya" Kasprzak's original [mrtg-rrd](https://www.fi.muni.cz/~kas/mrtg-rrd/) script. From Jan's site:

> "mrtg-rrd.cgi is a [CGI](http://www.w3.org/CGI/)/[FastCGI](http://www.fastcgi.com/) script for displaying [MRTG](http://oss.oetiker.ch/mrtg/) graphs from data in the [RRDtool](http://oss.oetiker.ch/rrdtool/) format. It can make your monitoring system faster because MRTG does not have to generate all the PNG files with graphs every 5 minutes or so. Instead of this the graphs are generated on-demand when the user wants to see them.
> 
> The main goal of this project is to generate the output similar to the MRTG native graphs as much as possible, providing the drop-in replacement to the MRTG-generated graphs. It reads the same configuration file as MRTG does, and it can understand most of the directive types in this configuration file. It can display single graph pages as well as the directory indexes referring to more graphs or subdirectories."

I continue to pursue the or original goal of providing a drop-in replacement for MRTG's generated pages & graphs.

Please read the [FAQ](FAQ) for further details.

LICENSE
-------

Copyright (C) 2001 Jan "Yenya" Kasprzak <kas@fi.muni.cz>
Copyright (C) 2009 Morgan Aldridge <morgant@makkintosshu.com>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

