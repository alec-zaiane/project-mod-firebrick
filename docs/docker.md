1. Make sure you have docker installed
2. copy the `.env.example` file to `.env` and fill in the values if you want to change them
3. run `docker compose build` to build the docker image
4. run `docker compose up -d && docker compose logs -f` to start the server and follow the logs (ctrl+C to exit)
5. run `docker compose exec -it socialnetwork sh` to enter the container
    - [OPTIONAL] run `python manage.py flush` to clear the database
6. run `python manage.py migrate` to apply the migrations
7. run `python manage.py createsuperuser` to create a superuser
8. Done :)
