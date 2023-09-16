from django.db import models
from account.models import Account
# Create your models here.


class FriendsList(models.Model):
    user = models.ForeignKey(
        Account, on_delete=models.CASCADE, null=True, blank=True, related_name="user")
    friends = models.ManyToManyField(
        Account, null=True, blank=True, related_name="friends")

    def __str__(self):
        return self.user.username

    def add_friend(self, account):
        """
        Add a new friend
        """
        if not account in self.friends.all():
            self.friends.add(account)
            self.save()

    def remove_friend(self, account):
        """
        Remove a friend
        """
        if account in self.friends.all():
            self.friends.remove(account)

    def unfriend(self, removee):
        """
        Initiate the action of unfriending someone
        """
        remover_friends_list = self  # person terminating the frienship

        # Remove friend from romover friends list
        remover_friends_list.remove_friend(removee)

        # Remove friend from removee friends list
        friends_list = FriendsList.objects.get(user=removee)
        friends_list.remove_friend(self.user)

    def is_mutual_friend(self, friend):
        """
        Is this a friend
        """
        if friend in self.friends.all():
            return True
        return False
