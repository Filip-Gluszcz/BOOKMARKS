from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# Create your models here.
class Action(models.Model):
    user = models.ForeignKey('auth.User', 
                             on_delete=models.CASCADE, 
                             related_name='actions', 
                             db_index=True)

    verb = models.CharField(max_length=255)

    target_ct = models.ForeignKey(ContentType, 
                                  on_delete=models.CASCADE, 
                                  blank=True, 
                                  null=True, 
                                  related_name='target_obj')

    target_id = models.PositiveIntegerField(blank=True, 
                                            null=True, 
                                            db_index=True)

    target = GenericForeignKey('target_ct', 
                               'target_id')

    created = models.DateTimeField(auto_now_add=True, 
                                   db_index=True)

    class Meta:
        ordering = ('-created',)