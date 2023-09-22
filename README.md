# Kashikally API

This is API is the backend of the Kashikally app.

It has been developed with Python (FastAPI) and PostgreSQL, and containerized using Docker.

## Requirements and installation

__Requirements__

* Docker (preferably 20.10.17+)

__Installation and usage__

1. Build Docker images

```console
$ docker-compose up -d --build

[+] Running 2/2
 ⠿ Container kashikally-db-1        Running                                                                  0.0s
 ⠿ Container kashikally-backend-1   Started                                                                  0.5s
```

2. You can check the API documentation and test it from [http://localhost:8000/docs](http://localhost:8000/docs)

3. You can access the admin site from [http://localhost:8000/admin/](http://localhost:8000/admin/)


## Next steps

1. Add Github Actions

2. Implement unit tests

3. Fix admin site (currently gives an error at the Products page)
