from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Collection, Product, OrderItem,Review
from .serializers import CollectionSerializer, ProductSerializer,ReviewSerializer
from rest_framework.viewsets import ModelViewSet



class ProductViewSet(ModelViewSet):
    serializer_class=ProductSerializer
    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        queryset=Product.objects.all()
        collection_id=self.request.query_params.get('collection_id')
        if collection_id is not None:
            queryset=queryset.filter(collection_id=collection_id)
        return queryset
    
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