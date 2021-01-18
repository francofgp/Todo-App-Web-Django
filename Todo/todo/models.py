from django.db import models
from django.contrib.auth.models import User


class Todo(models.Model):
    title = models.CharField(max_length=200)
    memo = models.TextField(blank=True)
    # cuando se hace un nuevo todo=automaticamente se crea la fecha y hora

    # esto no se muestra en el admin
    # si queremos que se muestre en el admin, tenemos que
    # ir al admin.py y agregar la clase TodoAdmin(admin.ModelAdmin),
    # esto es para que se vea en el admin, pero no lo podes modificar
    created = models.DateTimeField(auto_now_add=True)

    # para el django admin, para crear el objeto, tenes que poner
    # blank=True
    datecompleted = models.DateTimeField(null=True, blank=True)
    important = models.BooleanField(default=False)

    # relacionamos el Todo con el User, cada Todo tiene un User
    # osea foreign key

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
