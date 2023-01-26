from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,DestroyModelMixin
from rest_framework.response import Response
from .filters import ProductFilter
from .models import Collection, Product, OrderItem,Review,Cart,CartItem
from .serializers import CollectionSerializer, ProductSerializer,ReviewSerializer, CartSerializer, CartItemSerializer,AddCartItemSerializer,UpdateCartItemSerializer
from .pagination import DefaultPagination

class CartViewSet(CreateModelMixin, 
                  DestroyModelMixin,
                  GenericViewSet,
                  RetrieveModelMixin):
    queryset=Cart.objects.prefetch_related('items__product').all()
    serializer_class=CartSerializer
    
class CartItemViewSet(ModelViewSet):
    http_method_names=['get','patch','delete','post']
    def get_serializer_class(self):
        if self.request.method=='POST' :
            return AddCartItemSerializer
        elif self.request.method=='PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer
    def get_serializer_context(self):
        return {'cart_id':self.kwargs['cart_pk']}
    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).select_related('product')
    
class ProductViewSet(ModelViewSet):
    
    queryset=Product.objects.all()    
    serializer_class=ProductSerializer
    filter_backends=[DjangoFilterBackend, SearchFilter,OrderingFilter]
    filterset_class=ProductFilter 
    pagination_class=DefaultPagination
    
    search_fields=['title','description','collection__title']
    ordering_fields=['unit_price','last_update']


    def get_serializer_context(self):
        return {'request': self.request}

    
    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count()>0:
            return Response({'error': 'Product cannot be deleted because it is associated with an order item.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)
    
    
    

class CollectionViewSet(ModelViewSet):
    queryset=  Collection.objects.annotate(products_count=Count('products')).all()
    serializer_class=CollectionSerializer
    
    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=kwargs['pk']).count()>0:
            return Response({'error': 'Collection cannot be deleted because it includes one or more products.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)
    
    
class ReviewViewSet(ModelViewSet):
        queryset=Review.objects.all()
        serializer_class=ReviewSerializer
        def get_serializer_context(self):
             return {'product_id': self.kwargs['product_pk']}
        def get_queryset(self):
             return Review.objects.filter(product_id=self.kwargs['product_pk'])