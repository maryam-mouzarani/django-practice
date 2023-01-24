from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers


router= DefaultRouter()
router.register('products', views.ProductViewSet,basename='products')
router.register('collections',views.CollectionViewSet)


productRouter=routers.NestedDefaultRouter(router, 'products',lookup='product')

productRouter.register('reviews',views.ReviewViewSet, basename='product-reviews')
# URLConf
urlpatterns = router.urls+ productRouter.urls 