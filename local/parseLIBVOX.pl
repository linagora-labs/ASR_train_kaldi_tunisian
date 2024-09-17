#!/usr/bin/env perl


#Copyright (C) 2016, Linagora, Ilyes Rebai
#Email: irebai@linagora.com


$in_list = $ARGV[0];

open IL, $in_list;

while ($l = <IL>)
{
	chomp($l);
	$l =~ s/’/'/g;
	$l =~ s/'/' /g;
	$l =~ s/ – / /g;
	$l =~ s/–/ /g;
	$l =~ s/œ/oe/g;
	$l =~ s/ / /g;
	$l =~ s/aujourd' hui/aujourd'hui/g;
	$l =~ s/ encor / encore /g;
	$l =~ s/ mâtin / matin /g;
	$l =~ s/ plangô / plango /g;
	$l =~ s/ premiere / première /g;
	$l =~ s/ pére / père /g;
	$l =~ s/ quarant / quarante /g;
	$l =~ s/ qutre / quatre /g;
	$l =~ s/ rhythme / rythme /g;
	$l =~ s/ rhythmées / rythmées /g;
	$l =~ s/ shiraz / schiraz /g;
	$l =~ s/ sixème / sixième /g;
	$l =~ s/ tems / temps /g;
	$l =~ s/ égypte / egypte /g;
	$l =~ s/ “ //g;
	$l =~ s/ ” //g;
	$l =~ s/ m / monsieur /g;
	$l =~ s/ mm / messieurs /g;
	$l =~ s/ mr / monsieur /g;
	$l =~ s/ mosieu / monsieur /g;
	$l =~ s/ mme / madame /g;
	$l =~ s/ mlle / mademoiselle /g;
	$l =~ s/ & / et /g;
	$l =~ s/…//g;
	print "$l\n";
}
