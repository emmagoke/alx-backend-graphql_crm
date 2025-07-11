import django_filters
from django_filters import FilterSet, CharFilter, DateTimeFilter, NumberFilter
from .models import Customer, Product, Order


class CustomerFilter(FilterSet):
    name_icontains = CharFilter(field_name='name', lookup_expr='icontains')
    email_icontains = CharFilter(field_name='email', lookup_expr='icontains')
    created_at_gte = DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_lte = DateTimeFilter(field_name='created_at', lookup_expr='lte')
    phone_pattern = CharFilter(field_name='phone', lookup_expr='startswith')

    class Meta:
        model = Customer
        fields = {
            'name': ['icontains'],
            'email': ['icontains'], 
            'created_at': ['gte', 'lte'],
            'phone': ['startswith']
        }


class ProductFilter(FilterSet):
    name_icontains = CharFilter(field_name='name', lookup_expr='icontains')
    price_gte = NumberFilter(field_name='price', lookup_expr='gte')
    price_lte = NumberFilter(field_name='price', lookup_expr='lte')
    stock_gte = NumberFilter(field_name='stock', lookup_expr='gte')
    stock_lte = NumberFilter(field_name='stock', lookup_expr='lte')
    stock = NumberFilter(field_name='stock', lookup_expr='exact')
    low_stock = NumberFilter(field_name='stock', lookup_expr='lt')

    class Meta:
        model = Product
        fields = {
            'name': ['icontains'],
            'price': ['gte', 'lte'],
            'stock': ['gte', 'lte', 'exact', 'lt']
        }


class OrderFilter(FilterSet):
    total_amount_gte = NumberFilter(field_name='total_amount', lookup_expr='gte')
    total_amount_lte = NumberFilter(field_name='total_amount', lookup_expr='lte')
    order_date_gte = DateTimeFilter(field_name='order_date', lookup_expr='gte')
    order_date_lte = DateTimeFilter(field_name='order_date', lookup_expr='lte')
    customer_name = CharFilter(field_name='customer__name', lookup_expr='icontains')
    product_name = CharFilter(field_name='products__name', lookup_expr='icontains')
    product_id = NumberFilter(field_name='products__id', lookup_expr='exact')

    class Meta:
        model = Order
        fields = ['total_amount_gte', 'total_amount_lte', 'order_date_gte', 'order_date_lte', 'customer_name', 'product_name', 'product_id']
