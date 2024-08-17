from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView)
from .models import Post
from django.urls import reverse_lazy
from django.contrib.auth.mixins import (LoginRequiredMixin, UserPassesTestMixin)

class PostListView(ListView):
    template_name = "posts/list.html"
    model = Post

    # def get_queryset(self):
    #     return Post.objects.filter(author=self.request.user) //show only if u owner

class PostDetailView(DetailView):
    template_name = "posts/detail.html"
    model = Post

class PostCreateView(LoginRequiredMixin, CreateView):
    template_name = "posts/new.html"
    model = Post
    fields = ["title", "subtitle", "status", "body"]
    success_url = reverse_lazy("list")

    def form_valid(self, form):                     #instance author to new post
        form.instance.author = self.request.user
        return super().form_valid(form)
    
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = "posts/edit.html"
    model = Post
    fields = ["title", "subtitle", "body", "status"]
    success_url = reverse_lazy("list")  

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user

    def get_success_url(self):
        return reverse_lazy('detail', kwargs={'pk': self.object.pk})

class PostDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "posts/delete.html"
    model = Post
    success_url = reverse_lazy("list")