SHELL := /bin/bash

install-chrome:
	wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
	sudo apt --fix-broken install
	google-chrome-stable --version

download-chromedriver:
	wget "https://chromedriver.storage.googleapis.com/113.0.5672.63/chromedriver_linux64.zip" -O chromedriver_linux64.zip 

install-chromedriver:
	mkdir -p "chromedriver/stable"
	unzip -q "chromedriver_linux64.zip" -d "chromedriver/stable"
	chmod +x "chromedriver/stable/chromedriver"

create-venv:
	sudo apt install python3.8-venv -y
	python3 -m venv .venv

install-packages:
	pip install -r requirements.txt

scrape-indicator-input:
	python src/indicator.py

scrape-table:
	python src/scraper.py