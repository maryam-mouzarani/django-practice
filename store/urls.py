from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers


router= DefaultRouter()
router.register('products', views.ProductViewSet,basename='products')
router.register('collections',views.CollectionViewSet)
router.register('carts',views.CartViewSet)
router.register('customers',views.CustomerViewSet)
router.register('orders',views.OrderViewSet)


productRouter=routers.NestedDefaultRouter(router, 'products',lookup='product')

productRouter.register('reviews',views.ReviewViewSet, basename='product-reviews')
# URLConf

cartRouter=routers.NestedDefaultRouter(router, 'carts',lookup='cart')
cartRouter.register('items',views.CartItemViewSet, basename='carts-items')

urlpatterns = router.urls+ productRouter.urls +cartRouter.urls