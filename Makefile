all: privoxy tor setup

privoxy: privoxy.tar.gz
	tar -xvzf privoxy.tar.gz
	mv privoxy-* privoxy
	cd privoxy && autoheader && autoconf && ./configure
	make

privoxy.tar.gz:
	wget -O privoxy.tar.gz http://superb-dca2.dl.sourceforge.net/project/ijbswa/Sources/3.0.20%20%28beta%29/privoxy-3.0.20-beta-src.tar.gz

tor: tor.tar.gz
	tar -xvzf tor.tar.gz
	mv tor-* tor
	cd tor && ./configure && make

tor.tar.gz:
	wget -O tor.tar.gz 'https://www.torproject.org/dist/tor-0.2.4.21.tar.gz'


setup: privoxy tor
	python setup.py install
