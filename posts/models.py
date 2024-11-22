from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model

class Status(models.Model):
    """Modelo para los diferentes estados de las publicaciones."""
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=256)

    def __str__(self):
        return self.name

class PostObserver:
    """Clase base para observadores de cambios en publicaciones."""
    def notify(self, post):
        raise NotImplementedError("Debe implementarse en subclases")

class EmailNotificationObserver(PostObserver):
    """Observador para enviar notificaciones cuando se publica una entrada."""
    def notify(self, post):
        if post.status.name == "published":
            print(f"Notificación: La publicación '{post.title}' ha sido publicada.")
            # Aquí puedes agregar lógica para enviar correos.

class Post(models.Model):
    """Modelo principal para las publicaciones."""
    title = models.CharField(max_length=128)
    subtitle = models.CharField(max_length=256)
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE
    )
    status = models.ForeignKey(
        Status,
        on_delete=models.CASCADE
    )
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    _observers = []

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("detail", args=[self.id])

    def add_observer(self, observer):
        """Permite agregar observadores para este modelo."""
        self._observers.append(observer)

    def notify_observers(self):
        """Notifica a todos los observadores registrados."""
        for observer in self._observers:
            observer.notify(self)

    def save(self, *args, **kwargs):
        """Sobrescribimos el método save para notificar a los observadores."""
        super().save(*args, **kwargs)
        self.notify_observers()
