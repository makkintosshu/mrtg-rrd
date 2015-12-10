#!/usr/bin/perl -w
#
# $Id: mrtg-rrd.cgi,v 1.3 2001/12/17 17:17:42 kas Exp $
#
# mrtg-rrd.cgi: The script for generating graphs for MRTG statistics.
#
# Loosely modelled after the Rainer.Bawidamann@informatik.uni-ulm.de's
# 14all.cgi
#
#   Copyright (C) 2001 Jan "Yenya" Kasprzak <kas@fi.muni.cz>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#

use strict;

use POSIX qw(strftime);

# Location of RRDs.pm, if it is not in @INC
use lib '/usr/lib/perl5/5.00503/i386-linux';
use RRDs;

use vars qw(@config_files @all_config_files %targets %config $config_time);

# EDIT THIS to reflect all your MRTG config files
BEGIN { @config_files = qw(/home/fadmin/mrtg/mrtg.cfg); }

sub handler ($)
{
	my ($q) = @_;

	try_read_config();

	my ($stat, $ext) = ($q->path_info() =~
		/^\/(.+)(\.html|-(day|week|month|year)\.png)$/);

#	$stat ||= 'ares.fi.muni.cz.eth2';
#	$ext ||= '.html';

	print_error("Undefined statistics")
		unless defined $targets{$stat};

	my $tgt = $targets{$stat};

	common_args($stat, $tgt, $q);

	# We may be running under mod_perl or something. Do not destroy
	# the original settings of timezone.
	my $oldtz; 
	if (defined $tgt->{timezone}) {
		$oldtz = $ENV{TZ};
		$ENV{TZ} = $tgt->{timezone};
	}

	if ($ext eq '.html') {
		do_html($tgt);
	} elsif ($ext eq '-day.png') {
		do_image($tgt, 'day');
	} elsif ($ext eq '-week.png') {
		do_image($tgt, 'week');
	} elsif ($ext eq '-month.png') {
		do_image($tgt, 'month');
	} elsif ($ext eq '-year.png') {
		do_image($tgt, 'year');
	} else {
		print_error("Unknown extension");
	}
	$ENV{TZ} = $oldtz
		if defined $oldtz;
}

sub do_html($)
{
	my ($tgt) = @_;

	my @day   = do_image($tgt, 'day');
	my @week  = do_image($tgt, 'week');
	my @month = do_image($tgt, 'month');
	my @year  = do_image($tgt, 'year');

	http_headers('text/html', $tgt);
	print <<'EOF';
<HTML>
<HEAD>
<TITLE>
EOF
	print $tgt->{title} if defined $tgt->{title};
	print "</TITLE>\n";

	html_comments($tgt, 'd', @{$day[0]}) if $#day != -1;
	html_comments($tgt, 'w', @{$week[0]}) if $#week != -1;
	html_comments($tgt, 'm', @{$month[0]}) if $#month != -1;
	html_comments($tgt, 'y', @{$year[0]}) if $#year != -1;

	print $tgt->{addhead} if defined $tgt->{addhead};

	print "</HEAD>\n", $tgt->{bodytag}, "\n";
	
	print $tgt->{pagetop} if defined $tgt->{pagetop};

	unless (defined $tgt->{options}{noinfo}) {
		my @st = stat $tgt->{rrd};

		print "<HR>\nThe statistics were last updated ",
			strftime("<B>%A, %e %B, %T %Z</B>\n",
				localtime($st[9]));
	}

	html_graph($tgt, 'day', 'Daily', '5 Minute', \@day);
	html_graph($tgt, 'week', 'Weekly', '30 Minute', \@week);
	html_graph($tgt, 'month', 'Monthly', '2 Hour', \@month);
	html_graph($tgt, 'year', 'Yearly', '1 Day', \@year);

	print <<"EOF" unless defined $tgt->{options}{nolegend};
<HR><table WIDTH=500 BORDER=0 CELLPADDING=4 CELLSPACING=0>
<tr><td ALIGN=RIGHT><font SIZE=-1 COLOR="$tgt->{col1}">
<b>$tgt->{colname1} ###</b></font></td>
<td><font SIZE=-1>$tgt->{legend1}</font></td></tr> <tr><td ALIGN=RIGHT><font SIZE=-1 COLOR="$tgt->{col2}">
<b>$tgt->{colname2} ###</b></font></td>
<td><font SIZE=-1>$tgt->{legend2}</font></td></tr> </table>
EOF
	print <<"EOF" unless defined $tgt->{options}{nobanner};

<HR>
<table BORDER=0 CELLSPACING=0 CELLPADDING=0>
<tr>
<td WIDTH=63><a ALT="MRTG"
    HREF="http://ee-staff.ethz.ch/~oetiker/webtools/mrtg/mrtg.html"><img
BORDER=0 SRC="$config{icondir}/mrtg-l.png"></a></td>
<td WIDTH=25><a ALT=""
    HREF="http://ee-staff.ethz.ch/~oetiker/webtools/mrtg/mrtg.html"><img
BORDER=0 SRC="$config{icondir}/mrtg-m.png"></a></td>
<td WIDTH=388><a ALT=""
    HREF="http://ee-staff.ethz.ch/~oetiker/webtools/mrtg/mrtg.html"><img
BORDER=0 SRC="$config{icondir}/mrtg-r.png"></a></td>
</tr>
</table>
<spacer TYPE=VERTICAL SIZE=4>
<table BORDER=0 CELLSPACING=0 CELLPADDING=0 WIDTH=476>
<tr VALIGN=top>
<td ALIGN=LEFT><font FACE="Arial,Helvetica" SIZE=2>
version 2.9.17</font></td>
<td ALIGN=RIGHT><font FACE="Arial,Helvetica" SIZE=2>
<a HREF="http://ee-staff.ethz.ch/~oetiker/">Tobias Oetiker</a>
<a HREF="mailto:oetiker\@ee.ethz.ch">&lt;oetiker\@ee.ethz.ch&gt;</a>
</font></td>
</tr><tr>
<td></td>
<td ALIGN=RIGHT><font FACE="Arial,Helvetica" SIZE=2>
<and&nbsp;<a HREF="http://www.bungi.com">Dave&nbsp;Rand</a>&nbsp;<a HREF="mailto:dlr\@bungi.com">&lt;dlr\@bungi.com&gt;</a></font>
</td>
<tr VALIGN=top>
<td ALIGN=LEFT><font FACE="Arial,Helvetica" SIZE=2>
<A HREF=http://www.fi.muni.cz/~kas/mrtg-rrd/>mrtg-rrd.cgi version 0.1</A>
</font></td>
<td ALIGN=RIGHT><font FACE="Arial,Helvetica" SIZE=2>
<A HREF="http://www.fi.muni.cz/~kas/">Jan "Yenya" Kasprzak</A>
<A HREF="mailto:kas\@fi.muni.cz">&lt;kas\@fi.muni.cz&gt;</A>
</font></td>
</tr>
</table>
EOF
	print $tgt->{pagefoot} if defined $tgt->{pagefoot};
	print "\n", <<'EOF';
</body>
</html>
EOF

}

sub html_comments($$@)
{
	my ($tgt, $letter, @val) = @_;

	return if $#val == -1;

	print "<!-- maxin $letter ", int $val[1], " -->\n";
	print "<!-- maxout $letter ", int $val[3], " -->\n";
	print "<!-- avin $letter ", int $val[5], " -->\n";
	print "<!-- avout $letter ", int $val[0], " -->\n";
	print "<!-- cuin $letter ", int $val[2], " -->\n";
	print "<!-- cuout $letter ", int $val[4], " -->\n";
}


sub html_graph($$$$$)
{
	my ($tgt, $ext, $freq, $period, $params) = @_;

	return unless defined $tgt->{$ext};

	my @values = @{$params->[0]};
	my $x = $params->[1];
	my $y = $params->[2];

	$x *= $tgt->{xscale} if defined $tgt->{xscale};
	$y *= $tgt->{yscale} if defined $tgt->{yscale};

	my $kilo = $tgt->{kilo};
	my @kmg = split(',', $tgt->{kmg});

	my $fmt;
	if (defined $tgt->{options}{integer}) {
		$fmt = '%d';
	} else {
		$fmt = '%.1lf';
	}

	my @percent = do_percent($tgt, \@values);

	my @nv;
	for my $val (@values) {
		my @kmg1 = @kmg;

		for my $si (@kmg1) {
			if ($val < 10000) {
				push @nv, sprintf($fmt, $val) . " $si";
				last;
			}
			$val /= $kilo;
		}
	}
	@values = @nv;

	print "<HR>\n<B>\`$freq\' Graph ($period Average)</B><BR>\n";

	print '<IMG SRC="', $tgt->{url}, '-', $ext, '.png" WIDTH=', $x,
		' HEIGHT=', $y, ' ALT="', $freq,
		' Graph" VSPACE=10 ALIGN=TOP><BR>', "\n";
	print '<TABLE CELLPADDING=0 CELLSPACING=0>';
	print <<EOF if $tgt->{legendi} ne '';
    <TR>
	<TD ALIGN=RIGHT><SMALL>Max <FONT COLOR="$tgt->{col1}">$tgt->{legendi}</FONT></SMALL></TD>
	<TD ALIGN=RIGHT><SMALL>&nbsp;$values[1]$tgt->{shortlegend}$percent[1]</SMALL></TD>
	<TD WIDTH=5></TD>
	<TD ALIGN=RIGHT><SMALL>Average <FONT COLOR="$tgt->{col1}">$tgt->{legendi}</FONT></SMALL></TD>
	<TD ALIGN=RIGHT><SMALL>&nbsp;$values[3]$tgt->{shortlegend}$percent[3]</SMALL></TD>
	<TD WIDTH=5></TD>
	<TD ALIGN=RIGHT><SMALL>Current <FONT COLOR="$tgt->{col1}">$tgt->{legendi}</FONT></SMALL></TD>
	<TD ALIGN=RIGHT><SMALL>&nbsp;$values[5]$tgt->{shortlegend}$percent[5]</SMALL></TD>
    </TR>
EOF
	print <<EOF if $tgt->{legendo} ne '';
    <TR>
	<TD ALIGN=RIGHT><SMALL>Max <FONT COLOR="$tgt->{col2}">$tgt->{legendo}</FONT></SMALL></TD>
	<TD ALIGN=RIGHT><SMALL>&nbsp;$values[0]$tgt->{shortlegend}$percent[0]</SMALL></TD>
	<TD WIDTH=5></TD>
	<TD ALIGN=RIGHT><SMALL>Average <FONT COLOR="$tgt->{col2}">$tgt->{legendo}</FONT></SMALL></TD>
	<TD ALIGN=RIGHT><SMALL>&nbsp;$values[2]$tgt->{shortlegend}$percent[2]</SMALL></TD>
	<TD WIDTH=5></TD>
	<TD ALIGN=RIGHT><SMALL>Current <FONT COLOR="$tgt->{col2}">$tgt->{legendo}</FONT></SMALL></TD>
	<TD ALIGN=RIGHT><SMALL>&nbsp;$values[4]$tgt->{shortlegend}$percent[4]</SMALL></TD>
EOF
	if (defined $tgt->{options}{dorelpercent}) {
		print <<"EOF";
    </TR><TR>
	<TD ALIGN=RIGHT><SMALL>Max <FONT COLOR="$tgt->{col5}">&nbsp;Percentage:</FONT></SMALL></TD>
	<TD ALIGN=RIGHT><SMALL>&nbsp;$percent[6]</SMALL></TD>
	<TD WIDTH=5></TD>
	<TD ALIGN=RIGHT><SMALL>Average <FONT COLOR="$tgt->{col5}">&nbsp;Percentage:</FONT></SMALL></TD>
	<TD ALIGN=RIGHT><SMALL>&nbsp;$percent[7]</SMALL></TD>
	<TD WIDTH=5></TD>
	<TD ALIGN=RIGHT><SMALL>Current <FONT COLOR="$tgt->{col5}">&nbsp;Percentage:</FONT></SMALL></TD>
	<TD ALIGN=RIGHT><SMALL>&nbsp;$percent[8]</SMALL></TD>
EOF
	}
	print <<'EOF';
    </TR>
</TABLE>
EOF
}

sub do_percent($$)
{
	my ($tgt, $values) = @_;

	my @percent = ('', '', '', '', '', '', '', '', '');

	return @percent if defined $tgt->{options}{nopercent};

	for my $val (0..$#$values) {
		my $mx = ($val % 2 == 1) ? $tgt->{maxbytes1} : $tgt->{maxbytes2};
		next unless defined $mx;
		my $p = sprintf("%.1f", $values->[$val]*100/$mx);
		$percent[$val] = ' (' . $p . '%)';
	}

	if (defined $tgt->{options}{dorelpercent}) {
		for my $val (0..2) {
			$percent[6+$val] = sprintf("%.1f", 
				$values->[2*$val+1] * 100 / $values->[2*$val])
				if $values->[2*$val] > 0;
			$percent[6+$val] ||= 0;
			$percent[6+$val] .= ' %';
		}
	}
			
	@percent;
}

sub http_headers($$)
{
	my ($content_type, $target) = @_;

	print <<"EOF";
Content-Type: $content_type
Refresh: $config{refresh}
Pragma: no-cache
EOF
	# Expires header calculation stolen from CGI.pm
	print strftime("Expires: %a, %d %b %Y %H:%M:%S GMT\n",
		gmtime(time+$config{interval}));

	print "\n";
}

sub do_image($$$)
{
	my ($target, $ext) = @_;

	my $file = $target->{$ext};

	return unless defined $file;

	# Now the vertical rule at the end of the day
	my @t = localtime(time);
	$t[0] = $t[1] = $t[2] = 0;

	my $seconds;
	my $oldsec;
	my $back;

	if ($ext eq 'day') {
		$seconds = strftime("%s", @t);
		$back = 30*3600;	# 30 hours
		$oldsec = $seconds - 86400;
	} elsif ($ext eq 'week') {
		$seconds = strftime("%s", @t);
		$t[6] = ($t[6]+6) % 7;
		$seconds -= $t[6]*86400;
		$back = 8*86400;	# 8 days
		$oldsec = $seconds - 7*86400;
	} elsif ($ext eq 'month') {
		$t[3] = 1;
		$seconds = strftime("%s", @t);
		$back = 36*86400;	# 36 days
		$oldsec = $seconds - 30*86400; # FIXME (the right # of days!!)
	} elsif ($ext eq 'year') {
		$t[3] = 1;
		$t[4] = 0;
		$seconds = strftime("%s", @t);
		$back = 396*86400;	# 365 + 31 days
		$oldsec = $seconds - 365*86400; # FIXME (the right # of days!!)
	} else {
		print_error("Unknown file extension: $ext");
	}

	my @rv = RRDs::graph($file, '-s', "-$back", @{$target->{args}},
		"VRULE:$oldsec#ff0000", "VRULE:$seconds#ff0000");

	# In array context just return the values
	return @rv if wantarray;

	# Not in array context ==> print out the PNG file.
	http_headers('image/png', $target);
		
	open PNG, "<$file" or print_error("Can't open $file: $!");
	my $buf;
        # could be sendfile in Linux ;-)
        while(sysread PNG, $buf, 8192) {
                print $buf;
        }
	close PNG;
}

sub common_args($$$)
{
	my ($name, $target, $q) = @_;

	return @{$target->{args}} if defined @{$target->{args}};

	$target->{name} = $name;

	if (defined $target->{directory}) {
		$target->{directory} .= '/'
			unless $target->{directory} =~ /\/$/;
	} else {
		$target->{directory} = '';
	}

	$target->{url} = $q->url . '/' . $name;

	my $dir = $config{workdir};
	$dir = $config{logdir}
		if defined $config{logdir};

	$target->{rrd}   = $dir . '/' . $target->{directory} . $name . '.rrd';

	%{$target->{options}} = ()
		unless defined %{$target->{options}};

	$dir = $config{workdir};
	$dir = $config{imagedir}
		if defined $config{imagedir};

	$target->{suppress} ||= '';

	$target->{day}   = $dir . '/' . $target->{directory} . $name
		. '-day.png' unless $target->{suppress} =~ /d/;
	$target->{week}  = $dir . '/' . $target->{directory} . $name
		. '-week.png' unless $target->{suppress} =~ /w/;
	$target->{month} = $dir . '/' . $target->{directory} . $name
		. '-month.png' unless $target->{suppress} =~ /m/;
	$target->{year}  = $dir . '/' . $target->{directory} . $name
		. '-year.png' unless $target->{suppress} =~ /y/;

	$target->{maxbytes1} = $target->{maxbytes}
		if defined $target->{maxbytes} && !defined $target->{maxbytes1};

	$target->{maxbytes2} = $target->{maxbytes1}
		if defined $target->{maxbytes1} && !defined $target->{maxbytes2};

	my @args = ();

	push @args, '--lazy', '-c', 'FONT#000000', '-c',
		'MGRID#000000', '-c', 'FRAME#000000',
		'-g';

	$target->{background} = '#f5f5f5'
		unless defined $target->{background};

	push @args, '-c', 'BACK'. $target->{background};

	push @args, '-c', 'SHADEA' . $target->{background},
		'-c', 'SHADEB' . $target->{background}
		if defined $target->{options}{noborder};

	if (defined $target->{options}{noarrow}) {
		push @args, '-c', 'ARROW' . $target->{background};
	} else {
		push @args, '-c', 'ARROW#000000';
	}

	push @args, '-b', $target->{kilo}
		if defined $target->{kilo};

	push @args, '-w', $target->{xsize}
		if defined $target->{xsize};

	push @args, '-h', $target->{ysize}
		if defined $target->{ysize};

	my $scale = 1;
	
	if (defined $target->{options}->{perminute}) {
		$scale *= 60;
	} elsif (defined $target->{options}->{perhour}) {
		$scale *= 3600;
	}

	if (defined $target->{options}->{bits}) {
		$scale *= 8;
		$target->{ylegend} = 'Bits per second'
			unless defined $target->{ylegend};
		$target->{legend1} = 'Incoming Traffic in Bits per Second'
			unless defined $target->{legend1};
		$target->{legend2} = 'Outgoing Traffic in Bits per Second'
			unless defined $target->{legend2};
		$target->{shortlegend} = 'b/s'
			unless defined $target->{shortlegend};
	} else {
		$target->{ylegend} = 'Bytes per second'
			unless defined $target->{ylegend};
		$target->{legend1} = 'Incoming Traffic in Bytes per Second'
			unless defined $target->{legend1};
		$target->{legend2} = 'Outgoing Traffic in Bytes per Second'
			unless defined $target->{legend2};
		$target->{shortlegend} = 'B/s'
			unless defined $target->{shortlegend};
	}

	if ($scale > 1) {
		push @args, "DEF:in0=$target->{rrd}:ds0:AVERAGE",
			"CDEF:in=in0,$scale,*",
			"DEF:out0=$target->{rrd}:ds1:AVERAGE",
			"CDEF:out=out0,$scale,*";
	} else {
		push @args, "DEF:in=$target->{rrd}:ds0:AVERAGE",
			"DEF:out=$target->{rrd}:ds1:AVERAGE";
	}

	my $i=1;
	for my $coltext (split(/,/, $target->{colours})) {
		my ($text, $rgb) = ($coltext =~ /^([^#]+)(#[0-9a-fA-F]{6})$/);
		$target->{'col'.$i} = $rgb;
		$target->{'colname'.$i} = $text;
		$i++;
	}

	push @args, '-v', $target->{ylegend};

	push @args, 'AREA:in' . $target->{col1} . ':In',
		'LINE2:out' . $target->{col2} . ':Out';

	push @args, 'PRINT:out:MAX:%.1lf', 'PRINT:in:MAX:%.1lf',
		'PRINT:out:AVERAGE:%.1lf', 'PRINT:in:AVERAGE:%.1lf',
		'PRINT:out:LAST:%.1lf', 'PRINT:in:LAST:%.1lf';

	if (defined $target->{maxbytes1}) {
		$target->{maxbytes1} *= $scale;
		push @args, 'HRULE:' . $target->{maxbytes1} . '#cc0000';
	}

	if (defined $target->{maxbytes2}) {
		$target->{maxbytes2} *= $scale;
		push @args, 'HRULE:' . $target->{maxbytes2} . '#cccc00'
			if $target->{maxbytes2} != $target->{maxbytes1};
	}

	@{$target->{args}} = @args;

	@args;
}

sub try_read_config()
{
	my $read_cfg;
	if (!defined $config_time) {
		$read_cfg = 1;
	} else {
		for my $file (@all_config_files) {
			my @stat = stat $file;
			if ($config_time < $stat[9]) {
				$read_cfg = 1;
				last;
			}
		}
	}

	return unless $read_cfg;

	my %defaults = (
		xsize => 400,
		ysize => 100,
		kmg => ',k,M,G,T,P',
		kilo => 1000,
		bodytag => "<BODY BGCOLOR=#ffffff>\n",
		colours => 'GREEN#00cc00,BLUE#0000ff,DARK GREEN#006600,MAGENTA#ff00ff,AMBER#ef9f4f',
		legendi => '&nbsp;In:',
		legendo => '&nbsp;Out:',
	);

	%config = (
		refresh => 300,
		interval => 300,
		icondir => '.',
	);

	%targets = ();

	%{$targets{_}} = %defaults;
	%{$targets{'^'}} = ();
	%{$targets{'$'}} = ();

	@all_config_files = @config_files;

	for my $cfgfile (@config_files) {
		read_mrtg_config($cfgfile, \%defaults);
	}

	if (defined $config{pathadd}) {
		$ENV{PATH} .= ':'.$config{pathadd};
	}

#	if (defined $config{libadd}) {
#		use lib $config{libadd}
#	}

	$config_time = time;
}

sub read_mrtg_config($$);

sub read_mrtg_config($$)
{
	my ($file, $def) = @_;

	my %defaults = %$def;

	my @lines;

	open(CFG, "<$file") || print_error("Cannot open config file: $!");
	while (<CFG>) {
		chomp;                    # remove newline
		s/\s+$//;                 # remove trailing space
		s/\s+/ /g;                # collapse white spaces to ' '
		next if /^ *\#/;           # skip comment lines
		next if /^\s*$/;          # skip empty lines
		if (/^ \S/) {             # multiline options
			$lines[$#lines] .= $_;
		} else {
			push @lines, $_;
		}
	}
	close CFG;

	foreach (@lines) {
		if (/^([\w\d]+)\[(\S+)\] *: *(.*)$/) {
			my ($tgt, $opt, $val) = (lc($2), lc($1), $3);
			unless (exists $targets{$tgt}) {
				%{$targets{$tgt}} = %{$targets{_}};
			}
			if ($tgt eq '_' && $val eq '') {
				if ($defaults{$opt}) {
					$targets{_}{$opt} = $defaults{$opt};
				} else {
					delete $targets{_}{$opt};
				}
			} elsif (($tgt eq '^' || $tgt eq '$') && $val eq '') {
				delete $targets{$tgt}{$opt};
			} elsif ($opt eq 'options') {
				$val = lc($val);
				map { $targets{$tgt}{options}{$_} = 1 } ($val =~ m/([a-z]+)/g);
			} else {
				my $pre = $targets{'^'}{$opt}
					if defined $targets{'^'}{$opt};
				$pre ||= '';
				$targets{$tgt}{$opt} = $pre.$val;
				$targets{$tgt}{$opt} .= $targets{'$'}{$opt}
					if defined $targets{'$'}{$opt};
			}
			next;
		} elsif (/^Include *: *(\S*)$/) {
			push @all_config_files, $1;
			read_mrtg_config($1, $def);
			next;
		} elsif (/^([\w\d]+) *: *(\S*)$/) {
			my ($opt, $val) = (lc($1), lc($2));
			$config{$opt} = $val;
			next;
		}
		print_error("Parse error in $file near $_");
	}
}

sub dump_targets() {

	for my $tgt (keys %targets) {
		print "Target $tgt:\n";
		for my $opt (keys %{$targets{$tgt}}) {
			if ($opt eq 'options') {
				print "\toptions: ";
				for my $o1 (keys %{$targets{$tgt}{options}}) {
					print $o1, ",";
				}
				print "\n";
				next;
			}
			print "\t$opt: ", $targets{$tgt}{$opt}, "\n";
		}
	}
}

sub dump_config() {

	print "Config:\n";
	for my $opt (keys %config) {
		print $opt, ": ", $config{$opt}, "\n";
	}
}

sub print_error(@)
{
	print "Content-Type: text/plain\n\nError: ", join(' ', @_), "\n";
	exit 0;
}

#--BEGIN CGI--
#For CGI, use this:

use CGI;
my $q = new CGI;

handler($q);

#--END CGI--
#--BEGIN FCGI--
# For FastCGI, uncomment this and comment out the above:
#-# use FCGI;
#-# use CGI;
#-# 
#-# my $req = FCGI::Request();
#-# 
#-# while ($req->Accept >= 0) {
#-# 	my $q = new CGI;
#-# 	handler($q);
#-# }
#--END FCGI--

1;

