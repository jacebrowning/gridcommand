from django.db import models


class Game(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=4, blank=False, default='    ')
    owner = models.ForeignKey('auth.User', related_name='games')

    class Meta:
        ordering = ('created',)

COLOR_CHOICES = (
    ('red', "Red"),
    ('blue', "Blue"),
    ('teal', "Teal"),
    ('purple', "Purple"),
    ('yellow', "Yellow"),
    ('orange', "Orange"),
    ('green', "Green"),
    ('pink', "Pink"),
)


class Player(models.Model):
    code = models.CharField(max_length=4, blank=False)
    color = models.CharField(choices=COLOR_CHOICES, max_length=6)
    game = models.ForeignKey(
        Game,
        editable=False,
        related_name='players',
    )
