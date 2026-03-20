install:
	npm ci
	python3 -m pip install -r requirements.txt

build:
	npm run build

serve:
	npm run preview

clean:
	npm run clean
