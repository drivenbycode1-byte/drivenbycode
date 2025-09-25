import sys
import os

# 🔧 Agrega la carpeta src/ al PYTHONPATH
SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.insert(0, SRC_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dbc_project.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()


from dbc_app.models import Entry

# Carpeta donde se guardarán los .md
BASE_DIR = os.path.dirname(__file__)  # 👈 esto apunta a dbc_app/content/scripts

entries = Entry.objects.all()

for entry in entries:
    filename = f"{entry.title.replace(' ', '_').replace('/', '_')}.md"
    path = os.path.join(BASE_DIR, filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# {entry.title}\n\n{entry.text}")

