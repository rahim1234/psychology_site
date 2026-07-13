#!/bin/bash
# Deployment script for Ubuntu 22.04
# Run as root or with sudo

set -e

echo "=== Updating system ==="
sudo apt update && sudo apt upgrade -y

echo "=== Installing dependencies ==="
sudo apt install python3 python3-pip python3-venv nginx -y

echo "=== Creating project directory ==="
sudo mkdir -p /var/www/psychology_site
sudo chown $USER:$USER /var/www/psychology_site

echo "=== Copying project files ==="
cp -r . /var/www/psychology_site/
cd /var/www/psychology_site

echo "=== Creating virtual environment ==="
python3 -m venv venv
source venv/bin/activate

echo "=== Installing Python packages ==="
pip install -r requirements.txt

echo "=== Updating .env for production ==="
cat > .env << 'EOF'
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
DEBUG=False
ALLOWED_HOSTS=your_domain.com,localhost
EOF

echo "=== Running migrations ==="
python manage.py migrate

echo "=== Creating superuser ==="
python manage.py shell -c "
from accounts.models import User
if not User.objects.filter(username='rahim').exists():
    User.objects.create_superuser('rahim', 'rahim@example.com', 'R@him2024!StrongP@ss')
    print('Superuser created.')
else:
    print('Superuser already exists.')
"

echo "=== Collecting static files ==="
python manage.py collectstatic --noinput

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
echo "Login: rahim@example.com / R@him2024!StrongP@ss"
