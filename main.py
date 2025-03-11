# /// script
# dependencies = ["nanodjango", 'ipdb', "openai", "dotenv", "Pillow", "pdf2image"]
# ///

import base64
from openai import OpenAI
from datetime import datetime, timedelta
from nanodjango import Django
from django.shortcuts import render, get_object_or_404, redirect
from django.db import models
from django import forms
from django.utils import timezone
from django.template.defaulttags import register
from django.core.files import File
from dotenv import load_dotenv
import os
from pdf2image import convert_from_path, convert_from_bytes

load_dotenv()
api_key = os.getenv('OPENAI_KEY')
client = OpenAI(api_key = api_key)
default_prompt = "Please transcribe these handwritten notes into text?"

# app = Django(EXTRA_APPS=['django_q',])
app = Django()

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

    def __str__(self):
        return f"{self.category.description}, {self.description}"

    @property
    def double_number(self):
        return self.number * 2

@app.admin
class Record(models.Model):
    pdf_file = models.FileField(upload_to='uploads/', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    def __str__(self):
        return f"{self.created}: {self.pdf_file}"

    class Meta:
        ordering = ['-created']

@app.admin
class Translation(models.Model):
    record = models.ForeignKey(Record, on_delete=models.CASCADE, null=True)
    prompt = models.TextField(default=default_prompt, null=True, blank=True)
    results = models.TextField(default="Not yet translated.", null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    submitted = models.BooleanField(default=False)

    def __str__(self):
        if self.submitted:
            return f"RESULTS {self.results}"
        return f"UNSUBMITTED"

@app.route("/", name="index")
def index(request):
    records = Record.objects.all()
    context = {
        "records": records,
    }
    return render(request, "index.html", context)

@app.route("/record/<int:record_id>", name="record")
def record(request, record_id=None):
    if record_id is not None:
        record = get_object_or_404(Record, pk=record_id)
    context = {
        "record": record,
    }
    return render(request, "record.html", context)

@app.route("/convert/<int:record_id>", name="convert")
def record(request, record_id):
    record = get_object_or_404(Record, pk=record_id)
    images = convert_from_path(record.pdf_file.path, fmt="png")
    image_path = 'media/temp_image.png'
    images[0].save(image_path)
    with open(image_path, 'rb') as img_file:
        record.image.save(f"image_{record.pk}.png", File(img_file), save=False)
        record.save()
    
    return redirect("record", record_id=record_id)

class RecordModelForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = '__all__' # Includes all fields from the model
        # exclude = ['field_to_exclude'] # Excludes specific fields

if __name__ == "__main__":
    app.run()
