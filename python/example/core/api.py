from core.author_api import api as author_api
from django_bolt import BoltAPI

api = BoltAPI(prefix="/blogs")

# Mount author API (includes /authors and /blogs endpoints)
api.mount("/ms", author_api)





@api.post("/")
async def get_items(blog:BlogSerializer):

    print(blog)

    return {"asdf":"asdf"}

