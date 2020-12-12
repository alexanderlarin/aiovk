#!/bin/sh
openssl req -x509 -nodes -newkey rsa:2048 -keyout key.pem -out cert.pem -days 20000 -subj "/C=US/ST=Oregon/L=Portland/O=Company Name/OU=Org/CN=localhost"
