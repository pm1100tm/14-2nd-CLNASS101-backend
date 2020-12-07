# Generated by Django 3.1.3 on 2020-12-07 20:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Kit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('main_image_url', models.URLField(max_length=1000)),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('description', models.CharField(max_length=1000, null=True)),
            ],
            options={
                'db_table': 'kits',
            },
        ),
        migrations.CreateModel(
            name='KitSubImageUrl',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_url', models.URLField(max_length=1000)),
                ('kit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kit.kit')),
            ],
            options={
                'db_table': 'kit_sub_image_urls',
            },
        ),
        migrations.CreateModel(
            name='KitLike',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kit.kit')),
            ],
            options={
                'db_table': 'kit_likes',
            },
        ),
    ]
