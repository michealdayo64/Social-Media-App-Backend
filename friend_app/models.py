from django.db import models
from django.conf import settings
# Create your models here.


class FriendsList(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user", null=True)
    friends = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="friends")

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

    @property
    def get_cname(self):
        return "FriendsList"


class FriendRequest(models.Model):
    """
    A friend request consist of two main parts:
        1. SENDER:
            - Person sending/initiating the friend request
        2. RECIEVER:
            - Person recieving the friend request
    """
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sender")
    reciever = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reciever")
    is_active = models.BooleanField(blank=True, null=False, default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sender.username

    def accept(self):
        """
        Accept a friend request
        Update both SENSER and RECIEVER friend lists
        """
        reciever_friend_list = FriendsList.objects.get(user=self.reciever)
        if reciever_friend_list:
            reciever_friend_list.add_friend(self.sender)
            sender_friend_list = FriendsList.objects.get(user=self.sender)
            if sender_friend_list:
                sender_friend_list.add_friend(self.reciever)
                self.is_active = False
                self.save()

    def decline(self):
        """
        Decline a friend request
        It is "declined" by setting the 'is_active' field to false
        """
        self.is_active = False
        self.save()

    def cancel(self):
        """
        Cancel a friend request
        It is "cancelled" byy setting the 'is_active' field to False.
        This is only different with respect to "declining" through the notification that
        is generated.
        """

        self.is_active = False
        self.save()

    @property
    def get_cname(self):
        return "FriendRequest"
