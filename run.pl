#!/usr/bin/perl
use warnings;
use strict;
use Sys::Hostname qw(hostname);
use File::Basename;

main();
exit 0;

sub cores {
    chomp(my $cores = `cat /proc/cpuinfo | grep -c processor`);
    return $cores;
}

sub run {
    my $rc = system(@_);
    $rc == 0 or die "Failed to run @_";
}

sub main {
    my $cores = cores();
    my $hostname = hostname();
    my $dirname = dirname(__FILE__);
    mkdir "$dirname/results";
    my $gcp = eval { run ('sudo dmidecode -s system-product-name 2>/dev/null | grep "Google Compute Engine"') };
    run ("findmnt $dirname/results || /usr/bin/gcsfuse xenminer $dirname/results") if $gcp;
    run ("while [ true ]; do (cd $dirname; TQDM_DISABLE=1 venv/bin/python -u miner.py >> results/$hostname.$_ 2>&1; sleep 1); done &") for 1..$cores;
}
