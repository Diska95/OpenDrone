"""Data migration: forza un solo ruolo per utente.

Prima di questa migration la registrazione aggiungeva sempre 'customer'
ai roles dell'utente, e in alcuni casi un utente poteva trovarsi con
piu' ruoli (es. ['designer', 'customer']). Da ora in poi vale il
vincolo "un solo ruolo per utente".

Strategia di backfill - priorita' (precedenza):
  admin > designer > print_node > assembly_center > customer

Per ogni utente con piu' di un ruolo, manteniamo solo il piu' alto
in priorita' tra quelli presenti. Utenti gia' con un singolo ruolo non
vengono toccati. Utenti con roles=[] (caso edge) restano cosi'.
"""
from django.db import migrations


PRIORITY = ['admin', 'designer', 'print_node', 'assembly_center', 'customer']


def collapse_to_single_role(apps, schema_editor):
    User = apps.get_model('users', 'User')
    for user in User.objects.all():
        roles = user.roles or []
        if len(roles) <= 1:
            continue
        # Tieni il primo ruolo per priorita' tra quelli presenti
        chosen = next((r for r in PRIORITY if r in roles), None)
        if chosen:
            user.roles = [chosen]
            user.save(update_fields=['roles'])


def noop_reverse(apps, schema_editor):
    # Reversibile: non possiamo ripristinare i ruoli rimossi (informazione
    # persa). La reverse e' un no-op.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(collapse_to_single_role, noop_reverse),
    ]
