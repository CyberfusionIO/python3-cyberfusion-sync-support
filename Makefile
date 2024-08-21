PREFIX=$(CURDIR)/debian/

install: python3-cyberfusion-sync-support

python3-cyberfusion-sync-support: PKGNAME	:= python3-cyberfusion-sync-support
python3-cyberfusion-sync-support: PKGPREFIX	:= $(PREFIX)/$(PKGNAME)
python3-cyberfusion-sync-support: SDIR		:= python

python3-cyberfusion-sync-support:
	rm -rf $(CURDIR)/build
	python3 setup.py install --force --root=$(PKGPREFIX) --no-compile -O0 --install-layout=deb

clean:
	rm -rf $(PREFIX)/python3-cyberfusion-sync-support/
	rm -rf $(PREFIX)/*debhelper*
	rm -rf $(PREFIX)/*substvars
	rm -rf $(PREFIX)/files
	rm -rf $(CURDIR)/build
	rm -rf $(CURDIR)/src/*.egg-info
