from django import forms
from .models import Comment, Post, Category
from django_summernote.widgets import SummernoteWidget
from bs4 import BeautifulSoup


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("body",)
        widgets = {
            "body": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Write your comment here..."}
            )
        }


class EmailPostForm(forms.Form):
    name = forms.CharField(
        max_length=25, widget=forms.TextInput(attrs={"placeholder": "Your name"})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "Your email"})
    )
    to = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "Recipient's email"})
    )
    comments = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={"rows": 4, "placeholder": "Your comments (optional)"}
        ),
    )


class SearchForm(forms.Form):
    query = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Search posts..."})
    )


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "category", "tags", "body"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Enter post title"}),
            "category": forms.Select(attrs={"class": "form-control"}),
            "tags": forms.TextInput(
                attrs={"placeholder": "Enter tags separated by commas"}
            ),
            "body": SummernoteWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.all()
        self.fields["category"].required = False
        self.fields["category"].empty_label = "Select a category (optional)"
        if self.instance and self.instance.pk:
            self.fields["tags"].initial = ", ".join(self.instance.tags.names())

    def clean_title(self):
        title = self.cleaned_data["title"]
        if len(title) < 5:
            raise forms.ValidationError("Title must be at least 5 characters long.")
        return title

    def clean_body(self):
        body = self.cleaned_data["body"]
        soup = BeautifulSoup(body, "html.parser")
        text_content = soup.get_text(strip=True)
        if len(text_content) < 20:
            raise forms.ValidationError(
                "Post body must contain at least 20 characters of visible text."
            )
        return body

    def clean_tags(self):
        tags = self.cleaned_data.get("tags")
        if isinstance(tags, str):
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
            if len(tag_list) > 10:
                raise forms.ValidationError("You can only add up to 10 tags.")
        elif isinstance(tags, list):
            if len(tags) > 10:
                raise forms.ValidationError("You can only add up to 10 tags.")
        else:
            return []
        return tags
