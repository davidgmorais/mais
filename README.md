# Multimodal Authentication Integration System (MAIS)

Project developed in the scope of the course of biometrics in University of Aveiro 2021/22

## Objectives
<strike> The goal of the project is to develop a multimodal system that consists of:
- optical fingerprint reader [R307]
- face recognition [Pi camera]
- (optional) voice recognition [microphone]</strike>

~~In order to implement the project, we will use the Raspberry Pi platform, more specifically the 4B model.~~

During the first milestone of the project some issues in regard to both the Raspberry Pi and the fingerprint reader occurred, so the goals of the project were altered. The main goal of the project still was to develop a multimodal authentication system that consisted of:
- Face recognition [laptop camera]
- Voice recognition [laptop microphone]

Hence, the project shifted to a more localized approach using the built-in hardware available in the laptops themselves. 

## Bookmarked links
[Paddlet](https://padlet.com/emanuelkrzyszton/ladovfvxb9os68yo)

## Team
[93147	David Morais](https://github.com/davidgmorais)	

[106722	Emanuel Krzystoǹ](https://github.com/emanuelkrzyszton)

[105428	Gerson Carlos Marques Catito](https://github.com/GersonCatito)

## Installation
MAIS is available for Linux distros, and depends on an MySQL database for persistent data storage, which can be used through the `docker-compose.yml` present in the directory `./database`of the project or through a local installation of it.

### Prerequisites:
- [Python 3.6+](https://www.python.org/downloads/)
- [Pip3](https://pip.pypa.io/en/stable/installation/)
- [Docker Engine](https://docs.docker.com/engine/install/)
- [Docker compose](https://docs.docker.com/compose/install/)
- [MySQL (if not using the docker provided)](https://www.mysql.com/downloads/)

### Setting up
1. Either clone or download the project repository locally
2. In the project root directory create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Install the requirements
1. Install the requirements in the virtual environment through the `requirements.txt` file:
```bash
pip3 install -r requirements.txt
```

### Configure and run the database
1. On the root folder, open the directory `./database` where the database docker-compose file is located:
2. Build and run the database using docker-compose:
```bash
docker-compose up -d --build
```
**Note:** For subsequent uses, and after the image has been built, to restart the docker container you may simply run:
```bash
docker-compose up -d
```

### Alternative to docker-compose
Without docker, a MySQL database should be created instead, using the credentials present in the `docker-compose.yml` and with the schema shown in the file `mais.sql`, both available in the database directory.
