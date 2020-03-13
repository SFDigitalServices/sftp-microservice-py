# SFDS SFTP MICROSERVICE.PY [![CircleCI](https://badgen.net/circleci/github/SFDigitalServices/sftp-microservice-py/master)](https://circleci.com/gh/SFDigitalServices/sftp-microservice-py) [![Coverage Status](https://coveralls.io/repos/github/SFDigitalServices/sftp-microservice-py/badge.svg?branch=master)](https://coveralls.io/github/SFDigitalServices/sftp-microservice-py?branch=master)
This microservice facilitates the process to access and transfer data to a remote file system. 

### Sample Usage
Install Pipenv (if needed)
> $ pip install --user pipenv

Install included packages
> $ pipenv install

Start WSGI Server
> (sftp-microservice-py)$ pipenv run gunicorn 'service.microservice:start_service()'

Connect with cURL
> curl --location --request POST 'http://127.0.0.1:8000/sftp?dir=myfolder&filename=myfile.txt' 
--header 'ACCESS_KEY: 12345' 
--header 'X-SFTP-HOST: my-ftp-server.com' 
--header 'X-SFTP-HOST-KEY: hostkey' 
--header 'X-SFTP-USER: myuser' 
--header 'X-SFTP-PASSWORD: mypassword' 
--header 'Content-Type: text/plain' 
--data-raw 'hello world'

Get host key for your FTP server
> $ ssh-keyscan -t rsa my-ftp-server.com
my-ftp-server.com ssh-rsa xxxxxxxxxx


