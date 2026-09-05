from django.db import models

from core.models import BaseModel


class Country(BaseModel):
    country_short = models.CharField(max_length=10)
    country_long = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = "countries"
        verbose_name = "Country"
        verbose_name_plural = "Countries"
        indexes = [
            models.Index(fields=["country_short"], name="idx_country_short"),
            models.Index(fields=["country_long"], name="idx_country_long"),
        ]


class Province(BaseModel):
    province_name = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "provinces"
        verbose_name = "Province"
        verbose_name_plural = "Provinces"
        indexes = [models.Index(fields=["province_name"], name="idx_province_name")]

    def __str__(self):
        return self.province_name


class City(BaseModel):
    province = models.ForeignKey(
        Province, on_delete=models.CASCADE, related_name="cities"
    )
    city_name = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "cities"
        verbose_name = "City"
        verbose_name_plural = "Cities"
        indexes = [
            models.Index(fields=["city_name"], name="idx_city_name"),
            models.Index(fields=["province", "city_name"], name="idx_city_prov_city"),
        ]

    def __str__(self):
        return f"{self.city_name}, {self.province.province_name}"


class Language(BaseModel):
    language_name = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "languages"
        verbose_name = "Language"
        verbose_name_plural = "Languages"
        indexes = [models.Index(fields=["language_name"], name="idx_lang_name")]
