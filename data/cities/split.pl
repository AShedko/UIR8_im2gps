#!/usr/bin/perl
use DDP;

my @B= split '\n' ,`cat city_labels.txt | cut -f1 -d" "`;

for my $A ("test", "train", "val") {
	for my $b (@B) {
		`mkdir -p ./$A/$b`
	}	
	@C = split '\n', `cat $A.txt | cut -f1 -d" "`;
	for my $c (@C) {
		($e, $d) = split "\/", $c;
#		print "$c ./$A/$e/\n"
		`cp ./$c ./$A/$c`
	}
}
