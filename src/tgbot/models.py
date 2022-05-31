from __future__ import annotations
from typing import Union, Optional, Tuple
from django.db import models
from django.db.models import QuerySet, Manager
from telegram import Update
from telegram.ext import CallbackContext
from dtb.settings import pw, pw2, DEBUG, GENERATOR 
from tgbot.handlers.utils.info import extract_user_data_from_update
from tgbot.handlers.utils.encryption import encrypt
from utils.models import CreateUpdateTracker, nb, CreateTracker, GetOrNoneManager

class AdminUserManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_admin=True)

class User(CreateUpdateTracker):
    address = models.CharField(max_length=256)
    seed = models.CharField(max_length=512)
    user_id = models.IntegerField(null=True, blank=True)  # telegram_id
    username = models.CharField(max_length=32, **nb)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256, **nb)
    language_code = models.CharField(max_length=8, help_text="Telegram client's lang", **nb)
    is_admin = models.BooleanField(default=False)

    objects = GetOrNoneManager()  # user = User.objects.get_or_none(user_id=<some_id>)
    admins = AdminUserManager()  # User.admins.all()
    def __str__(self):
        return f'@{self.username}' if self.username is not None else f'{self.user_id}'
    
    @classmethod
    def create_by_seed(cls, address, seed, username):
        data = {'address' : address, 'seed' : seed, 'username' : username}
        cls.objects.create(**data)   

    @classmethod
    def get_user(cls, update: Update, context: CallbackContext) -> Tuple[User, bool]:
        data = extract_user_data_from_update(update)
        if "user_id" in data: # 1) Check user_id since some users don't have any username
            user_id = int(data["user_id"])
            user = cls.objects.filter(user_id=user_id).first()
            option = 1
        if str(user) == 'None' and "username" in data: # 2) Only when the user's account was created because of a tip we don't know their user_id since tips work with usernames
            username = str(data["username"]).replace("@", "").strip().lower()
            user = cls.objects.filter(username__iexact=username).first()
            option = 2
        if str(user) == 'None': # If the user can't be found by username nor user_id
            address = pw.Address(GENERATOR, pywaves=pw2)
            address._generate()
            data["address"] = address.address
            data["seed"] = encrypt(address.seed.encode('utf8'))
            u = cls.objects.create(**data)
            return (u, True)
        elif option == 1:
            u, _ = cls.objects.update_or_create(user_id=user_id, defaults=data)
        elif option == 2:
            u, _ = cls.objects.update_or_create(username=username, defaults=data)
        return (u, False)

    @classmethod
    def get_user_by_username(cls, username: Union[str, int]) -> Optional[User]:
        """ Search user in DB, return User or None if not found """
        username = str(username).replace("@", "").strip().lower()
        return cls.objects.filter(username__iexact=username).first()

    @property
    def tg_str(self) -> str:
        if self.username:
            return f'@{self.username}'
        return f"{self.first_name} {self.last_name}" if self.last_name else f"{self.first_name}"