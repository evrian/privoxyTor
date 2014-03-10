#!/bin/bash

python setup.py install;
var="$(python -c 'from distutils.sysconfig import get_python_lib; print(get_python_lib())')";
var=$var'/privoxy*';
var=$(echo $var)'/privoxytor';
echo $var;

wget -O $var/bin/privoxy.tar.gz http://superb-dca2.dl.sourceforge.net/project/ijbswa/Sources/3.0.20%20%28beta%29/privoxy-3.0.20-beta-src.tar.gz;
wget -O $var/bin/tor.tar.gz 'https://www.torproject.org/dist/tor-0.2.4.21.tar.gz';

tar -xvzf $var/bin/tor.tar.gz -C $var/bin;
tar -xvzf $var/bin/privoxy.tar.gz -C $var/bin;

mv $var/bin/privoxy-* $var/bin/privoxy;
cd $var/bin/privoxy && autoheader && autoconf && ./configure && make;

mv $var/bin/tor-* $var/bin/tor;
cd $var/bin/tor && ./configure && make;

rm $var/bin/tor.tar.gz $var/bin/privoxy.tar.gz;
