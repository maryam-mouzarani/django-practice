from decimal import Decimal
from store.models import Product, Collection, Review,Cart,CartItem
from rest_framework import serializers
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum,F
class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']

    products_count = serializers.IntegerField()

class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields=['id','title','unit_price']
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'slug', 'inventory', 'unit_price', 'price_with_tax', 'collection']

    price_with_tax = serializers.SerializerMethodField(
        method_name='calculate_tax')

    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.1)



class CartItemSerializer(serializers.ModelSerializer):
    product=SimpleProductSerializer()   
    total_price=serializers.SerializerMethodField(method_name='calc_total_price')
    class Meta:
        model=CartItem
        fields=['id','cart_id','product','quantity','total_price']
        
    def calc_total_price(self,crtItm:CartItem):
        return crtItm.product.unit_price*crtItm.quantity
class CartSerializer(serializers.ModelSerializer):
    id=serializers.UUIDField(read_only=True)
    class Meta:
        model = Cart
        fields = ['id','items','whole_price']
        
    items=CartItemSerializer(many=True, read_only=True)
    whole_price=serializers.SerializerMethodField(method_name='calculate_whole_price')
    def calculate_whole_price(self,crt:Cart):
        return sum([item.quantity*item.product.unit_price  for item in crt.items.all()])
class ReviewSerializer(serializers.ModelSerializer):
    
        class Meta:
           model=Review
           fields=['id','date','name','description' ]
        def create(self, validated_data):
            product_ids=self.context['product_id']
            return Review.objects.create(product_id=product_ids, **validated_data)           