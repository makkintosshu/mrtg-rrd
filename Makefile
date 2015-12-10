# $Id: Makefile,v 1.6 2003/03/14 13:42:09 kas Exp $

FILES = COPYING FAQ TODO Makefile mrtg-rrd.cgi ChangeLog

TARGETS = mrtg-rrd.fcgi

VERSION = 0.6

all: $(TARGETS)

mrtg-rrd.fcgi: mrtg-rrd.cgi
	-rm -f mrtg-rrd.fcgi
	sed -e '/^#--BEGIN CGI--/,/^#--END CGI--/d' -e '/^#--BEGIN FCGI--/,/^#--END FCGI--/s/^#-# //' <mrtg-rrd.cgi >mrtg-rrd.fcgi
	chmod +x mrtg-rrd.fcgi

clean:
	-rm -f $(TARGETS)

dist:
	rm -rf mrtg-rrd-$(VERSION)
	mkdir mrtg-rrd-$(VERSION)
	cp $(FILES) mrtg-rrd-$(VERSION)
	tar cf - mrtg-rrd-$(VERSION) | gzip -9 > mrtg-rrd-$(VERSION).tar.gz
	-rm -rf mrtg-rrd-$(VERSION)

