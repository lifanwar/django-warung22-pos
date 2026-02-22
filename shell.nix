{ pkgs ? import <nixpkgs> {} }:

let
  python = pkgs.python311;
in
pkgs.mkShell {
  name = "django-dev-shell";

  buildInputs = [
    python
    pkgs.python311Packages.pip
    pkgs.nodejs_20
    pkgs.git
  ];

  shellHook = ''
    echo "==> Activating virtualenv in venv/ (if it exists)..."
    if [ -d "venv" ]; then
      source venv/bin/activate
      echo "==> Virtualenv venv/ activated."
    else
      echo "==> venv/ does not exist, creating it..."
      ${python}/bin/python -m venv venv
      source venv/bin/activate
      echo "==> Virtualenv venv/ created and activated."
    fi

    echo "==> Installing requirements.txt (if it exists)..."
    if [ -f "requirements.txt" ]; then
      pip install -r requirements.txt
    else
      echo "==> requirements.txt not found, skipping install."
    fi

    # Function to create an app in apps/<appname>
    startapp () {
      if [ -z "$1" ]; then
        echo "Usage: startapp <appname>"
        return 1
      fi
      local APP_NAME="$1"
      echo "==> Creating Django app: apps/''${APP_NAME}"
      mkdir -p "apps"
      python manage.py startapp "''${APP_NAME}" "apps/''${APP_NAME}"
    }

    # Tailwind aliases
    alias tw-install="python manage.py tailwind install"
    alias tw-watch="python manage.py tailwind start"

    # Runserver alias
    alias run="python manage.py runserver 0.0.0.0:8000"

    echo
    echo "==> Django development environment ready."
    echo "   - Virtualenv: venv/"
    echo "   - Useful commands:"
    echo "       startapp <appname>    # python manage.py startapp <appname> apps/<appname>"
    echo "       tw-install            # python manage.py tailwind install"
    echo "       tw-watch              # python manage.py tailwind start"
    echo "       run                   # python manage.py runserver 0.0.0.0:8000"
    echo
  '';
}
