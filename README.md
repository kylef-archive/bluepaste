# [Bluepaste](https://bluepaste.herokuapp.com)

[Bluepaste](https://bluepaste.herokuapp.com) is an API Blueprint paste service. 

## Development Environment

You can configure a development environment with the following:

**NOTE**: *These steps assume you have Python along with [pip](https://pip.pypa.io/en/latest/installing.html) and [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html) installed.*

```bash
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ export DATABASE_URL="sqlite:///$(pwd)/development.sqlite"
$ export JWT_KEY="secret"
$ invoke migrate
```

### Running the server

```bash
$ gunicorn bluepaste:wsgi --log-file -
```

## Deploying on Heroku

Click the button below to automatically set up the Bluepaste and deploy Bluepaste to your own Heroku instance.

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy?template=https://github.com/kylef/bluepaste)

## License

Bluepaste is released under the MIT license. See [LICENSE](LICENSE).
