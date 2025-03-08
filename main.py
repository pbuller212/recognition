# /// script
# dependencies = ["nanodjango", 'django-colorfield', 'ipdb', "openai", "dotenv"]
# ///

import base64
from openai import OpenAI
from datetime import datetime, timedelta
from nanodjango import Django
from django.shortcuts import render, get_object_or_404
from django.db import models
from django.utils import timezone
from django.template.defaulttags import register
from dotenv import load_dotenv
import os


load_dotenv()
api_key = os.getenv('OPENAI_KEY')

app = Django()

# Needs to be imported after instantiating the app object or will cause settings error
from colorfield.fields import ColorField


@register.filter
def get_item(dictionary, key):
    if dictionary is None or isinstance(dictionary, str) or key is None:
        return ""
    val = dictionary.get(key)
    return val if val is not None else ""


@app.admin
class ItemCategory(models.Model):
    description = models.CharField(default="", null=True, blank=True, max_length=50)

    def __str__(self):
        return f"{self.description}"


@app.admin
class Item(models.Model):
    description = models.CharField(default="", null=True, blank=True, max_length=50)
    category = models.ForeignKey(ItemCategory, on_delete=models.CASCADE, null=True)
    active = models.BooleanField(default=True)
    number = models.IntegerField(default=0, null=True)
    display_color = ColorField(default="#FFFFFF")

    def __str__(self):
        return f"{self.category.description}, {self.description}"

    @property
    def double_number(self):
        return self.number * 2


@app.route("/", name="index")
def index(request):
    items = Item.objects.filter(active=True).order_by("description")
    context = {
        "items": items,
    }
    return render(request, "index.html", context)


@app.route("/item/<int:item_id>", name="item_detail")
def item_detail(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    context = {
        "item": item,
    }
    return render(request, "item.html", context)


if __name__ == "__main__":
    app.run()
