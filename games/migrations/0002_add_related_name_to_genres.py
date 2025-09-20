# Generated manually to add related_name to genres field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='genres',
            field=models.ManyToManyField(blank=True, related_name='games', to='games.genre', verbose_name='Жанры'),
        ),
    ]
