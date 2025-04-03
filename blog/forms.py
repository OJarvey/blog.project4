from django import forms
from .models import Comment, Post, Category
from bs4 import BeautifulSoup
from cloudinary.forms import CloudinaryFileField
from ckeditor.widgets import CKEditorWidget


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
    featured_image = CloudinaryFileField(
        options={
            "folder": "blog_featured_images",
            "transformation": [
                {"width": 1870, "height": 1250, "crop": "fill"},
            ],
        },
        required=False,
    )

    class Meta:
        model = Post
        fields = ["title", "category", "tags", "body", "featured_image"]
        widgets = {"body": CKEditorWidget(config_name="default")}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.all()
        self.fields["category"].required = False
        self.fields["category"].empty_label = "Select a category (optional)"
        if self.instance and self.instance.pk:
            self.fields["tags"].initial = ", ".join(self.instance.tags.names())

    def clean_title(self):
        title = self.cleaned_data["title"]
        if len(title) < 3:
            raise forms.ValidationError("Title must be at least 3 characters long.")

        qs = Post.objects.filter(title__iexact=title)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("A post with this title already exists.")

        return title

    def clean_body(self):
        body = self.cleaned_data["body"]
        soup = BeautifulSoup(body, "html.parser")
        text_content = soup.get_text(strip=True)
        if len(text_content) < 10:
            raise forms.ValidationError(
                "Post body must contain at least 10 characters of visible text."
            )
        return body

    def clean_tags(self):
        tags = self.cleaned_data.get("tags")
        if isinstance(tags, str):
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
            if len(tag_list) > 5:
                raise forms.ValidationError("You can only add up to 5 tags.")
        elif isinstance(tags, list):
            if len(tags) > 5:
                raise forms.ValidationError("You can only add up to 5 tags.")
        else:
            return []
        return tags
