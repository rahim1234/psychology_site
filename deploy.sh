#!/bin/bash
# Deployment script for Ubuntu 22.04
# Run as a regular user with sudo privileges.

set -e

echo "=== Updating system ==="
sudo apt update && sudo apt upgrade -y

echo "=== Installing dependencies ==="
sudo apt install python3 python3-pip python3-venv nginx -y

echo "=== Creating project directory ==="
sudo mkdir -p /var/www/psychology_site
sudo chown "$USER":"$USER" /var/www/psychology_site

echo "=== Copying project files ==="
cp -r . /var/www/psychology_site/
cd /var/www/psychology_site

echo "=== Creating virtual environment ==="
python3 -m venv venv
source venv/bin/activate

echo "=== Installing Python packages ==="
pip install -r requirements.txt

if [ ! -f .env ]; then
    echo "=== Creating .env from .env.example ==="
    cp .env.example .env
    GENERATED_SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
    # Use a different sed delimiter (#) since the generated key can contain '/'.
    sed -i "s#^SECRET_KEY=.*#SECRET_KEY=${GENERATED_SECRET_KEY}#" .env
    sed -i "s/^DEBUG=.*/DEBUG=False/" .env
    sed -i "s/^ALLOWED_HOSTS=.*/ALLOWED_HOSTS=your_domain.com/" .env
    echo ""
    echo "!!! IMPORTANT !!!"
    echo "A .env file was generated with a random SECRET_KEY, but you still need to"
    echo "edit /var/www/psychology_site/.env to set ALLOWED_HOSTS and your real"
    echo "EMAIL_* (SMTP) settings before the site can send verification emails."
    echo ""
else
    echo "=== .env already exists, leaving it untouched ==="
fi

echo "=== Running migrations ==="
python manage.py migrate

echo "=== Collecting static files ==="
python manage.py collectstatic --noinput

echo "=== Creating admin (therapist) account ==="
echo "You will now be prompted to create the admin/therapist login interactively."
echo "This account is used to review clients, test results, and session notes."
python manage.py createsuperuser

echo "=== Setting up Gunicorn ==="
sudo cp /var/www/psychology_site/gunicorn.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn

echo "=== Setting up Nginx ==="
sudo cp /var/www/psychology_site/nginx.conf /etc/nginx/sites-available/psychology_site
sudo ln -sf /etc/nginx/sites-available/psychology_site /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

echo "=== Done! ==="
echo "Your site should now be live at http://your_domain.com"
echo "Admin panel: http://your_domain.com/admin/"
echo "Remember to edit .env with your real domain and SMTP credentials, then:"
echo "  sudo systemctl restart gunicorn"
