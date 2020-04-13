# SFDS SFTP MICROSERVICE.PY [![CircleCI](https://badgen.net/circleci/github/SFDigitalServices/sftp-microservice-py/master)](https://circleci.com/gh/SFDigitalServices/sftp-microservice-py) [![Coverage Status](https://coveralls.io/repos/github/SFDigitalServices/sftp-microservice-py/badge.svg?branch=master)](https://coveralls.io/github/SFDigitalServices/sftp-microservice-py?branch=master)
This microservice facilitates the process to access and transfer data to a remote file system. 

### How to run the service locally
Install Pipenv (if needed)

```$ pip install --user pipenv```

Install included packages

```$ pipenv install```

Start WSGI Server

```(sftp-microservice-py)$ pipenv run gunicorn 'service.microservice:start_service()'```

### How to use the service
In order to send your file you'll need the host key for your destination server. To get this value for X-SFTP-HOST-KEY run:

```$ ssh-keyscan -t rsa my-ftp-server.com```
The response is your host key. It will look like:

```my-ftp-server.com ssh-rsa xxxxxxxxxx```

The `ACCESS_KEY` is needed to connect with the sftp-microservice, and is set as an environment variable locally or on Heroku. 

Send a file via cURL:

```
curl --location --request POST 'http://127.0.0.1:8000/sftp?remotepath=<<path to destination directory>>&filename=myfile.txt' 
--header 'ACCESS_KEY: 12345' 
--header 'X-SFTP-HOST: my-ftp-server.com' 
--header 'X-SFTP-HOST-KEY: hostkey' 
--header 'X-SFTP-USER: myuser' 
--header 'X-SFTP-PASSWORD: mypassword' 
--header 'Content-Type: text/plain' 
--data-raw 'hello world'
```

Send a file using Python:
```
filename = <<path to file locally>>
files = {'file': (filename, open(filename, 'rb'), 'text/plain', {'Expires': '0'})}

headers = {
  'ACCESS_KEY': SFDS_SFTP_ACCESS_KEY,
  'X-SFTP-HOST': SFTP_HOSTNAME,
  'X-SFTP-HOST-KEY': SFTP_HOST_KEY,
  'X-SFTP-USER': SFTP_USERNAME,
  'X-SFTP-PASSWORD': SFTP_PASSWORD,
  'Content-Type': 'text/plain'
}

params = {
  'remotepath': <<path to destination directory>>,
  'filename': '<<desired filename at destination>>'
}

r = requests.post(
    'http://127.0.0.1:8000/sftp',
    files=files,
    headers=headers,
    params=params)
```



