
####Build docker image locally
    $ docker-compose build
####Start services
    $ docker-compose up
####Scale Celery workers
    $ docker-compose scale worker=5

####Explore
* Service should be available in [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
* API documentation in swagger json format is in [http://127.0.0.1:8000/api-docs](http://127.0.0.1:5000/api-docs)
* You can use swagger-ui in [http://127.0.0.1:8080/](http://127.0.0.1:8080/) to render the api-docs.
* You can use Celery monitoring (Flower) in [http://127.0.0.1:5555/](http://127.0.0.1:5555/).

####Development

