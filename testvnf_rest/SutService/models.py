import random
# from __future__ import unicode_literals

from django.db import models

def generate_sutId():
  return random.randint(0, 100000000000)

class Sut(models.Model):
  A = 'A'
  U = 'U'
  F = 'F'
  STATUS_CHOICES = (
    (A, 'Available'),
    (U, 'Unavailable'),
    (F, 'Failed'),
  )
  version = models.CharField(max_length=20, null=True)
  sutId = models.CharField(max_length=20, default=generate_sutId, unique=True)
  sutStatus = models.CharField(max_length=15, choices=STATUS_CHOICES, default=A)

  class Meta:
    ordering = ('version', 'sutStatus')

  def __str__(self):
    return "{}:{}".format(self.sutType, self.version)

  @property
  def name(self):
    return str(self)
