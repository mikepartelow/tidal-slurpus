IMAGE_TAG=tidal-playlists
MOUNT=-v`pwd`/app:/app

build:
	docker buildx build -t $(IMAGE_TAG) .

fmt: build
	docker run $(MOUNT) -ti $(IMAGE_TAG) /bin/bash -c 'black .'

lint: build
	docker run $(MOUNT) -ti $(IMAGE_TAG) /bin/bash -c 'flake8 --max-line-length 120 . && pylint --recursive y . && 	black --check .'

shell: build
	docker run $(MOUNT) -ti $(IMAGE_TAG) /bin/bash

run: build
	docker run $(MOUNT) -ti $(IMAGE_TAG)
