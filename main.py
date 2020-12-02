import os
import yaml

from webapp.app import create_app

secret_key = os.environ.get("SECRET_KEY", None)

if not secret_key:  # SECRET_KEY is set in github secrets
    with open("./secret.yaml") as f:
        secrets = yaml.load(f, Loader=yaml.SafeLoader)["env_variables"]
    secret_key = secrets["SECRET_KEY"]
assert secret_key is not None, "Failed to get secret key from environ or secret.json"

from werkzeug.middleware.profiler import ProfilerMiddleware

config = {"SECRET_KEY": secret_key, "PROFILE": True}

if os.environ.get("DEV_OVERRIDE_USER"):
    config["DEV_OVERRIDE_USER"] = os.environ["DEV_OVERRIDE_USER"]

app = create_app(config)
app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])


if __name__ == "__main__":
    app.env = "development"
    app.run(host="127.0.0.1", port=8080, debug=True, ssl_context="adhoc")
