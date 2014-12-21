from django.db import models


class Game(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=4, blank=False, default='    ')
    owner = models.ForeignKey('auth.User', related_name='games')

    class Meta:
        ordering = ('created',)
