
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from store.models import Customer

#a signal handler:
#a decorator to tell django this function should be called when a user model is saved:
#this function is called only after saving an instance of User model in AUTH_USER_MODEL
@receiver(post_save, sender=settings.AUTH_USER_MODEL )
def create_customer_for_new_user(sender, **kwargs):
    if kwargs['created']: # if a new model instance is created 
        Customer.objects.create(user=kwargs['instance'])
    
