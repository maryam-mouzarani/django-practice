from decimal import Decimal
from store.models import Product, Collection, Review,Cart,CartItem,Customer
from rest_framework import serializers
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum,F

class  UpdateCartItemSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=CartItem
        fields=['quantity']
    
class  AddCartItemSerializer(serializers.ModelSerializer):
    product_id=serializers.IntegerField()
    
    class Meta:
        model=CartItem
        fields=['id','product_id','quantity']
    def save(self, **kwargs):
        cart_id=self.context['cart_id']
        product_id=self.validated_data['product_id']
        quantity=self.validated_data['quantity']
        
        try:
            cart_item=CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity+=quantity
            cart_item.save()
            self.instance=cart_item
        except CartItem.DoesNotExist:
            self.instance=CartItem.objects.create(cart_id=cart_id, **self.validated_data)
        
        return self.instance
    def validate_product_id(self,value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('No product with this id exist')
        return value        
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

class CustomerSerializer(serializers.ModelSerializer):
    user_id=serializers.IntegerField(read_only=True)

    class Meta:
        model=Customer
        fields=['id','user_id', 'phone','birth_date','membership']


