import pytest
from django.template import Template, Context, TemplateSyntaxError
from django.urls.exceptions import NoReverseMatch
from django_bolt import BoltAPI

def test_bolt_url_tag_resolution():
    """Test standard named route resolution."""
    api = BoltAPI()
    
    @api.get("/users/{id}", name="user-detail")
    def user_detail(req, id: int):
        return {"id": id}
        
    template = Template("{% load bolt_urls %}{% bolt_url 'user-detail' id=123 %}")
    rendered = template.render(Context())
    assert rendered == "/users/123"

def test_bolt_url_multiple_params():
    """Test resolution with multiple parameters."""
    api = BoltAPI()
    
    @api.get("/posts/{post_id}/comments/{comment_id}", name="comment-detail")
    def comment_detail(req, post_id: int, comment_id: int):
        return {}
        
    template = Template("{% load bolt_urls %}{% bolt_url 'comment-detail' post_id=10 comment_id=20 %}")
    rendered = template.render(Context())
    assert rendered == "/posts/10/comments/20"

def test_bolt_url_missing_name():
    """Test error when route name is not found."""
    api = BoltAPI()
    template = Template("{% load bolt_urls %}{% bolt_url 'missing-route' %}")
    
    with pytest.raises(NoReverseMatch) as excinfo:
        template.render(Context())
    assert "Bolt URL 'missing-route' not found" in str(excinfo.value)

def test_bolt_url_missing_param():
    """Test error when parameter is missing."""
    api = BoltAPI()
    
    @api.get("/users/{id}", name="user-detail")
    def user_detail(req, id: int):
        return {}
        
    template = Template("{% load bolt_urls %}{% bolt_url 'user-detail' %}")
    
    with pytest.raises(NoReverseMatch) as excinfo:
        template.render(Context())
    assert "Missing argument" in str(excinfo.value)

def test_view_named_route():
    """Test named route using @api.view decorator."""
    api = BoltAPI()
    from django_bolt.views import APIView
    
    @api.view("/profile", name="user-profile")
    class ProfileView(APIView):
        def get(self):
            pass
            
    template = Template("{% load bolt_urls %}{% bolt_url 'user-profile' %}")
    rendered = template.render(Context())
    assert rendered == "/profile"

def test_viewset_named_route_auto_generation():
    """Test automatic name generation for ViewSets."""
    api = BoltAPI()
    from django_bolt.views import ViewSet
    
    @api.viewset("/items", name="items")
    class ItemViewSet(ViewSet):
        def list(self): pass
        def retrieve(self, pk): pass
        
    # Test list route
    template_list = Template("{% load bolt_urls %}{% bolt_url 'items-list' %}")
    assert template_list.render(Context()) == "/items"
    
    # Test retrieve route
    template_detail = Template("{% load bolt_urls %}{% bolt_url 'items-retrieve' pk=99 %}")
    assert template_detail.render(Context()) == "/items/99"
