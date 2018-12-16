#!/bin/sh
openssl req -x509 -nodes -newkey rsa:1024 -keyout key.pem -out cert.pem -days 2000 -subj "/C=US/ST=Oregon/L=Portland/O=Company Name/OU=Org/CN=localhost"
