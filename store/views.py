from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin,UpdateModelMixin,RetrieveModelMixin,DestroyModelMixin
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny,IsAdminUser,DjangoModelPermissions

from .filters import ProductFilter
from .models import Collection, Product, OrderItem,Review,Cart,CartItem,Customer,Order
from .serializers import CollectionSerializer, ProductSerializer,ReviewSerializer, CartSerializer, \
                        CartItemSerializer,AddCartItemSerializer,UpdateCartItemSerializer,CustomerSerializer, OrderSerializer, OrderCreateSerializer,OrderUpdateSerializer
from .pagination import DefaultPagination
from .permissions import IsAdminOrReadOnly, FullDjangoModelPermission,ViewHistoryPermission
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
    permission_classes=[IsAdminOrReadOnly]
    
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
    permission_classes=[IsAdminOrReadOnly]
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


class CustomerViewSet(ModelViewSet):
    queryset=Customer.objects.all()
    serializer_class=CustomerSerializer
    permission_classes=[IsAdminUser]



    @action(detail=True, permission_classes=[ViewHistoryPermission])
    def history(self,request, pk):
        return Response('ok')


    @action(detail=False, methods=['GET','PUT'] ,permission_classes=[IsAuthenticated])
    def me(self,request):
        customer=Customer.objects.get(user_id=request.user.id)
        if request.method=='GET':
            serializer=CustomerSerializer(customer)
            return Response(serializer.data)
       
        elif request.method=='PUT':
            serializer=CustomerSerializer(customer, data= request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

class OrderViewSet(ModelViewSet):
    http_method_names=['get','post','patch','delete', 'head','options']
    def get_permissions(self):
        if self.request.method in [ 'PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    def get_serializer_class(self):
        if self.request.method=='POST':
            return OrderCreateSerializer   
        elif self.request.method=='PATCH':
            return OrderUpdateSerializer 
        return OrderSerializer

    def create(self, request,  *args, **kwargs):
        serializer= OrderCreateSerializer(
                    data=request.data, 
                    context={'user_id':self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order=serializer.save()
        serializer=OrderSerializer(order)
        return Response(serializer.data)

   

    def get_queryset(self):
        user=self.request.user

        if user.is_staff:
            return Order.objects.all()
        customer_id=Customer.objects.only('id').get(user_id=user.id)
        return Order.objects.filter(customer_id=customer_id)
