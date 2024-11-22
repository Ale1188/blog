from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Post, Status

# ============================
# PATRÓN: Estrategia
# ============================

class StatusFilterStrategy:
    """Clase base para estrategias de filtrado."""
    def filter(self, queryset, user=None):
        raise NotImplementedError("Debe implementarse en la subclase")

class PublishedFilterStrategy(StatusFilterStrategy):
    """Estrategia para filtrar publicaciones publicadas."""
    def filter(self, queryset, user=None):
        return queryset.filter(status=Status.objects.get(name="published"))

class DraftFilterStrategy(StatusFilterStrategy):
    """Estrategia para filtrar publicaciones en borrador de un usuario específico."""
    def filter(self, queryset, user):
        return queryset.filter(status=Status.objects.get(name="draft"), author=user)

class ArchivedFilterStrategy(StatusFilterStrategy):
    """Estrategia para filtrar publicaciones archivadas."""
    def filter(self, queryset, user=None):
        return queryset.filter(status=Status.objects.get(name="archived"))

# ============================
# VISTAS BASADAS EN ESTRATEGIA
# ============================

class PostListView(ListView):
    """Vista genérica para listar publicaciones."""
    template_name = "posts/list.html"
    model = Post
    filter_strategy = None  # Esta será definida por las subclases

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = Post.objects.all().order_by("created_on").reverse()

        # Aplicamos la estrategia de filtrado
        if self.filter_strategy:
            context["post_list"] = self.filter_strategy.filter(queryset, self.request.user)
        return context

class PublishedPostListView(PostListView):
    """Vista para listar publicaciones publicadas."""
    filter_strategy = PublishedFilterStrategy()

class DraftPostListView(LoginRequiredMixin, PostListView):
    """Vista para listar borradores del usuario actual."""
    filter_strategy = DraftFilterStrategy()

class ArchivedPostListView(LoginRequiredMixin, PostListView):
    """Vista para listar publicaciones archivadas."""
    filter_strategy = ArchivedFilterStrategy()

# ============================
# VISTA PARA EL DETALLE
# ============================

class PostDetailView(DetailView):
    """Vista para mostrar el detalle de una publicación."""
    template_name = 'posts/detail.html'
    model = Post

# ============================
# PATRÓN: Observador
# ============================

class PostObserver:
    """Clase base para observadores de cambios en publicaciones."""
    def notify(self, post):
        raise NotImplementedError("Debe implementarse en subclases")

class EmailNotificationObserver(PostObserver):
    """Observador para enviar notificaciones por correo."""
    def notify(self, post):
        if post.status.name == "published":
            print(f"Notificación: La publicación '{post.title}' ha sido publicada.")
            # Aquí agregarías lógica para enviar el correo.

# ============================
# VISTAS PARA CREAR, EDITAR Y ELIMINAR
# ============================

class PostCreateView(LoginRequiredMixin, CreateView):
    """Vista para crear nuevas publicaciones."""
    template_name = 'posts/new.html'
    model = Post
    fields = ['title', 'subtitle', 'body', 'status']

    def form_valid(self, form):
        form.instance.author = self.request.user
        post = form.save()

        # Agregamos un observador para notificar cuando se publique
        post.add_observer(EmailNotificationObserver())
        return super().form_valid(form)

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Vista para eliminar publicaciones."""
    template_name = "posts/delete.html"
    model = Post
    success_url = reverse_lazy("list")

    def test_func(self):
        # Validamos que solo el autor pueda eliminar la publicación
        post = self.get_object()
        return post.author == self.request.user

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Vista para editar publicaciones existentes."""
    template_name = "posts/edit.html"
    model = Post
    fields = ['title', 'subtitle', 'body', 'status']

    def test_func(self):
        # Validamos que solo el autor pueda editar la publicación
        post = self.get_object()
        return post.author == self.request.user

class PostUpdateToDraftView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Vista para cambiar el estado de una publicación a 'draft'."""
    model = Post
    template_name = "posts/update_status.html"
    fields = ['status']

    def form_valid(self, form):
        # Cambia el estado a 'draft' al guardar
        form.instance.status = Status.objects.get(name="draft")
        return super().form_valid(form)

    def test_func(self):
        # Validamos que el usuario sea el autor o tenga permisos de staff
        post = self.get_object()
        return post.author == self.request.user or self.request.user.is_staff

    def get_success_url(self):
        # Redirige al detalle del post después de actualizar el estado
        return reverse_lazy('detail', kwargs={'pk': self.object.pk})

# ============================
# PATRÓN: Fábrica
# ============================

class PostFactory:
    """Fábrica para crear publicaciones con diferentes estados iniciales."""
    @staticmethod
    def create_post(author, title, body, status_name="draft"):
        status = Status.objects.get(name=status_name)
        return Post.objects.create(author=author, title=title, body=body, status=status)
