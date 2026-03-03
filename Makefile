PREFIX ?= /usr/local/bin

install:
	cp alldebrid-dl $(PREFIX)/alldebrid-dl
	chmod +x $(PREFIX)/alldebrid-dl
	@echo "Installed to $(PREFIX)/alldebrid-dl"

uninstall:
	rm -f $(PREFIX)/alldebrid-dl
	@echo "Removed from $(PREFIX)/alldebrid-dl"
