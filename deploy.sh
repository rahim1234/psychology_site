#!/bin/bash
# Deployment script for Ubuntu 22.04
# Run as a regular user with sudo privileges.

set -e

echo "=== Updating system ==="
sudo apt update && sudo apt upgrade -y

echo "=== Installing dependencies ==="
sudo apt install python3 python3-pip python3-venv nginx redis-server -y

echo "=== Enabling Redis (shared rate-limit cache across gunicorn workers) ==="
sudo systemctl enable redis-server
sudo systemctl start redis-server

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
    # get_random_string() (alnum-only charset) is used instead of
    # get_random_secret_key() because the latter can contain '#', '&', or
    # other sed/shell-special characters that break the substitution below
    # no matter which delimiter is chosen. Alnum-only is still cryptographically
    # secure for SECRET_KEY at this length.
    GENERATED_SECRET_KEY=$(python3 -c "from django.utils.crypto import get_random_string; print(get_random_string(50))")
    sed -i "s#^SECRET_KEY=.*#SECRET_KEY=${GENERATED_SECRET_KEY}#" .env
    sed -i "s/^DEBUG=.*/DEBUG=False/" .env
    sed -i "s/^ALLOWED_HOSTS=.*/ALLOWED_HOSTS=your_domain.com/" .env
    sed -i "s#^REDIS_URL=.*#REDIS_URL=redis://127.0.0.1:6379/1#" .env
    echo ""
    echo "!!! IMPORTANT !!!"
    echo "A .env file was generated with a random SECRET_KEY, but you still need to"
    echo "edit /var/www/psychology_site/.env to set ALLOWED_HOSTS and your real"
    echo "SMS_BACKEND / SMS_API_URL / SMS_API_KEY / SMS_SENDER_NUMBER (sms.ir or"
    echo "Kavenegar) before the site can send the phone verification codes used by"
    echo "registration, login, and password reset. EMAIL_* is optional and not"
    echo "required for verification."
    echo ""
else
    echo "=== .env already exists, leaving it untouched ==="
fi

echo "=== Creating media directories ==="
# media/ holds public uploads served directly by nginx; private_media/ holds
# files served only through profiles.views.protected_media (access-controlled).
# Both are gitignored and must be created on every fresh deploy.
mkdir -p /var/www/psychology_site/media
mkdir -p /var/www/psychology_site/private_media
sudo chown -R www-data:www-data /var/www/psychology_site/media /var/www/psychology_site/private_media
sudo chmod -R 755 /var/www/psychology_site/media
sudo chmod -R 750 /var/www/psychology_site/private_media

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
