from core.models import Author, Blog
from django_bolt import BoltAPI
from django_bolt.serializers import ModelSerializer

api = BoltAPI()


class AuthorSerializer(ModelSerializer):
    class Meta:
        model = Author
        fields = ["id", "name", "email", "bio", "created_at"]
        read_only = {"id", "created_at"}


class BlogSerializer(ModelSerializer):
    class Meta:
        model = Blog
        fields = ["id", "name", "description", "status", "author"]
        read_only = {"id"}


# Author endpoints
@api.get("/")
async def get_authors() -> list[AuthorSerializer]:
    return [author async for author in Author.objects.all()]


@api.get("/{author_id}")
async def get_author(author_id: int) -> AuthorSerializer:
    return await Author.objects.aget(id=author_id)


@api.post("/")
async def create_author(author: AuthorSerializer) -> AuthorSerializer:
    new_author = Author(
        name=author.name,
        email=author.email,
        bio=author.bio,
    )
    await new_author.asave()
    return new_author


# Blog endpoints
@api.get("/blogs")
async def get_blogs() -> list[BlogSerializer]:
    return [blog async for blog in Blog.objects.filter(status="published")]


@api.get("/blogs/{blog_id}")
async def get_blog(blog_id: int) -> BlogSerializer:
    return await Blog.objects.aget(id=blog_id)
