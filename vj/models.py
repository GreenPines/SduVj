# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


class Contest(models.Model):
    contestid = models.AutoField(primary_key=True)
    contestname = models.CharField(max_length=45)
    contestpro = models.CharField(max_length=255)
    contest_s_time = models.DateTimeField()
    contest_l_time = models.IntegerField()
    contest_admin = models.IntegerField()
 
    class Meta:
        managed = False
        db_table = 'contest'

class Problem(models.Model):
    proid = models.AutoField(primary_key=True)
    originoj = models.CharField(max_length=10)
    problemid = models.CharField(max_length=10)
    problemurl = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    timelimit = models.CharField(max_length=50)
    memorylimit = models.CharField(max_length=50)
    description = models.TextField()
    input = models.TextField()
    output = models.TextField()
    sampleinput = models.TextField()
    sampleoutput = models.TextField()
    updatetime = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'problem'


class Status(models.Model):
    runid = models.AutoField(primary_key=True)
    user = models.ForeignKey(User)
    pro = models.ForeignKey(Problem)
    code = models.TextField()
    lang = models.IntegerField(blank=True, null=True)
    result = models.CharField(max_length=50)
    timec = models.CharField(max_length=50, blank=True, null=True)
    memoryc = models.CharField(max_length=50, blank=True, null=True)
    time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'status'

