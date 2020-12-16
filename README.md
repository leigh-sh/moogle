# Moogle

## Stack
- Python, Flask, Redis

## Docker Instructions
docker-compose build 

docker-compose up -d 


## Run in browser
GET http://localhost:8080/spec

view the openapi documentation (can be pasted into any swagger editor)

GET http://localhost:8080/GetProxy?country_code=<country_code>

get proxy by country_code (us/uk)

POST http://localhost:8080/ReportError

report an invalid proxy
request requires a json body of the following format:
{
  "country_code": "<country_code>",
  "ip": "\<ip\>"
}
