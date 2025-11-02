


from django_bolt import BoltAPI

from core.models import Blog
import msgspec


api = BoltAPI(prefix="/blogs") #slash is required



class BlogSerializer(msgspec.Struct):
    
    name : str
    body: str
    status: str

@api.get("/")
async def get_blogs() -> BlogSerializer:
    
    return Blog.objects.filter(status="published")
    



@api.post("/")
async def get_items():
    
    pass


