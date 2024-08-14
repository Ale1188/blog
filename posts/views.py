from django.views.generic import ListView, DetailView, CreateView
from .models import Post
from django.urls import reverse_lazy

class PostListView(ListView):
    template_name = "posts/list.html"
    model = Post

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)

class PostDetailView(DetailView):
    template_name = "posts/detail.html"
    model = Post

class PostCreateView(CreateView):
    template_name = "posts/new.html"
    model = Post
    fields = ["title", "subtitle", "status", "body"]
    success_url = reverse_lazy("list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)