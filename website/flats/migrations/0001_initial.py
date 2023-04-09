# Generated by Django 4.1.5 on 2023-04-09 13:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AllFlatsLastPrice',
            fields=[
                ('flat_id', models.IntegerField(primary_key=True, serialize=False)),
                ('address', models.CharField(max_length=255, verbose_name='Адрес')),
                ('floor', models.IntegerField(blank=True, null=True, verbose_name='Этаж')),
                ('rooms', models.IntegerField(blank=True, null=True, verbose_name='Количество комнат')),
                ('area', models.FloatField(blank=True, null=True, verbose_name='Площадь')),
                ('finishing', models.BooleanField(blank=True, null=True, verbose_name='С отделкой')),
                ('settlement_date', models.DateField(blank=True, null=True, verbose_name='Заселение')),
                ('url_suffix', models.CharField(max_length=127, verbose_name='Продолжение URL к адресу ЖК')),
                ('project_id', models.IntegerField(unique=True)),
                ('city', models.CharField(max_length=127, verbose_name='Город')),
                ('name', models.CharField(max_length=127, verbose_name='ЖК')),
                ('url', models.CharField(max_length=255, verbose_name='URL')),
                ('price', models.IntegerField(verbose_name='Цена')),
                ('booking_status', models.CharField(max_length=15, verbose_name='Бронь')),
            ],
            options={
                'db_table': 'all_flats_last_price',
                'ordering': ['price'],
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Flat',
            fields=[
                ('flat_id', models.IntegerField(primary_key=True, serialize=False)),
                ('address', models.CharField(blank=True, max_length=255, null=True, verbose_name='Адрес')),
                ('floor', models.IntegerField(blank=True, null=True, verbose_name='Этаж')),
                ('rooms', models.IntegerField(blank=True, null=True, verbose_name='Количество комнат')),
                ('area', models.FloatField(blank=True, null=True, verbose_name='Площадь')),
                ('finishing', models.BooleanField(blank=True, null=True, verbose_name='С отделкой')),
                ('bulk', models.CharField(blank=True, max_length=127, null=True, verbose_name='Корпус')),
                ('settlement_date', models.DateField(blank=True, null=True, verbose_name='Заселение')),
                ('url_suffix', models.CharField(max_length=127, verbose_name='Продолжение URL к адресу ЖК')),
                ('data_created', models.DateField(auto_now_add=True, verbose_name='Опубликовано')),
                ('data_closed', models.DateField(blank=True, null=True, verbose_name='Снята с продажи')),
            ],
            options={
                'verbose_name': 'Квартира',
                'verbose_name_plural': 'Квартиры',
                'db_table': 'flat',
                'ordering': ['rooms'],
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('project_id', models.IntegerField(primary_key=True, serialize=False)),
                ('city', models.CharField(max_length=127, verbose_name='Город')),
                ('name', models.CharField(max_length=127, verbose_name='ЖК')),
                ('url', models.CharField(blank=True, max_length=255, null=True, verbose_name='URL')),
                ('metro', models.CharField(blank=True, max_length=127, null=True, verbose_name='Метро')),
                ('time_to_metro', models.IntegerField(blank=True, null=True, verbose_name='Время до метро')),
                ('latitude', models.FloatField(blank=True, null=True, verbose_name='Широта')),
                ('longitude', models.FloatField(blank=True, null=True, verbose_name='Долгота')),
                ('address', models.CharField(blank=True, max_length=255, null=True, verbose_name='Адрес')),
                ('data_created', models.DateField(auto_now_add=True, verbose_name='Опубликовано')),
                ('data_closed', models.DateField(blank=True, null=True, verbose_name='Снят с продажи')),
            ],
            options={
                'verbose_name': 'Жилой Комплекс',
                'verbose_name_plural': 'Жилые Комплексы',
                'db_table': 'project',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Price',
            fields=[
                ('price_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('benefit_name', models.CharField(blank=True, max_length=127, null=True, verbose_name='Ценовое предложение')),
                ('benefit_description', models.CharField(blank=True, max_length=255, null=True, verbose_name='Описание')),
                ('price', models.IntegerField(verbose_name='Цена')),
                ('meter_price', models.IntegerField(blank=True, null=True, verbose_name='Цена за метр')),
                ('booking_status', models.CharField(blank=True, max_length=15, null=True, verbose_name='Бронь')),
                ('data_created', models.DateField(auto_now_add=True, verbose_name='Опубликовано')),
                ('flat', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='prices', to='flats.flat')),
            ],
            options={
                'verbose_name': 'Цена',
                'verbose_name_plural': 'Цены',
                'db_table': 'price',
                'ordering': ['-data_created'],
            },
        ),
        migrations.AddField(
            model_name='flat',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='flats.project'),
        ),
    ]
