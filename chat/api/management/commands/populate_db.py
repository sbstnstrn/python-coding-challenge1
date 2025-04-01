import random
from api.models import User, Chat, Message
from django.core.management.base import BaseCommand
from django.utils import lorem_ipsum


class Command(BaseCommand):
    help = 'Creates dummy application data'

    def handle(self, *args, **kwargs):

        admin = User.objects.filter(username='admin').first()
        if not admin:
            admin = User.objects.create_superuser(username='admin', password='test')

        staff = User.objects.filter(username='staff').first()
        if not staff:
            staff = User.objects.create_user(username='staff', password='test', is_staff=True)

        user = User.objects.filter(username='user').first()
        if not user:
            user = User.objects.create_user(username='user', password='test')

        another_user = User.objects.filter(username='another_user').first()
        if not another_user:
            another_user = User.objects.create_user(username='another_user', password='test')

        chats = Chat.objects.all()
        if chats:
            print('Database already populated.')
            return
        
        # Create 2 random chats
        chat1 = Chat.objects.create(user=user)

        # create 10 random messages in chat1
        use_staff_user = True
        for _ in range(10):
            Message.objects.create(
                user=staff if use_staff_user else user,
                chat=chat1,
                content=lorem_ipsum.words(random.randint(5, 15))
            )
            use_staff_user = not use_staff_user
        

        chat2 = Chat.objects.create(user=another_user)

        # create 10 random messages in chat2
        use_staff_user = True
        for _ in range(10):
            Message.objects.create(
                user=staff if use_staff_user else another_user,
                chat=chat2,
                content=lorem_ipsum.words(random.randint(5, 15))
            )
            use_staff_user = not use_staff_user




    
        
