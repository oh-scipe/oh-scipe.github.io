install:
	npm install

build:
	node scripts/copyOptimizeImages.js
	python3 build.py

serve:
	python3 -m http.server 8008

clean:
	rm -f *.htm
	rm -rf initiatives
