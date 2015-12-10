# $Id: Makefile,v 1.1 2001/12/17 15:38:07 kas Exp $

FILES = COPYING FAQ TODO Makefile mrtg-rrd.cgi

TARGETS = mrtg-rrd.fcgi

VERSION = 0.1

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

