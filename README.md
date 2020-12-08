![CI](https://github.com/tomhamiltonstubber/dundjeon-finder/workflows/CI/badge.svg)
[![coverage](https://codecov.io/gh/tomhamiltonstubber/dundjeon-finder/branch/main/graph/badge.svg)](https://codecov.io/gh/tomhamiltonstubber/dundjeon-finder)

# Dungeon Finder

Dungeon Finder (TBC) will be a web app built by @codetopixels and @tomhamiltonstubber to provide an easy way for 
Dungeons & Dragons players to match with Game Masters (also known as Dungeon Masters, or DMs for short). 
Players will be able to view a list of games that have been created by DMs, filterable by a number of 
different attributes. Players will then be able to rate and review their DM.

Built with Django3

## To run locally

Create a virtualenv and install requirements with

```shell
make install-dev
```

To run the server for the first time run 

```shell
python ./manage reset_database
```

This not only creates the database but will also give you demo data to muck around with.

The run the server with:

```shell
python ./manage.py runserver
```

Changes to the code will cause the app to rebuild so you don't need to worry.

To load and watch static files (JS/SCSS) for changes, run `yarn-watch`. When you're running for the first time, run 
`yarn install`. The SCSS files in `static/scss/` will be compiled into `.css` files in `static/dist`. JavaScript in `static/js` 
will be compiled and minified into `static/dist`.

## Setup Postgres

**If you haven't already got Postgresql installed, you need to do that:**

```shell
sudo apt install postgresql-client postgresql postgresql-contrib postgresql-server-dev-12
```

Login to the postgres server

```shell
sudo -u postgres psql postgres
```

On OSX you may have to login to the default psql user and create a new user manually,

```shell
psql
CREATE USER postgres;
ALTER USER postgres WITH SUPERUSER;
```

Change the password for the "postgres" user

    \password postgres

(then enter the password "waffle" twice)

Exit postgres with `\q`.

You can avoid having to enter the password for postgres by setting up a default password

    echo "localhost:5432:*:postgres:waffle" >> .pgpass
    chmod 600 .pgpass

You can then connect to the database

    psql -h localhost -U postgres
    \q
