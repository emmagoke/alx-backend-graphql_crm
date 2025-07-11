import graphene
from graphene_django import DjangoObjectType
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction
import re
from decimal import Decimal

from .models import Customer, Product, Order

# -- GraphQL Types --
# Maps Django models to GraphQL types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ('id', 'name', 'email', 'phone', 'created_at')


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'stock', 'created_at')


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ('id', 'customer', 'products', 'total_amount', 'order_date', 'created_at')


# -- Query --
# The basic query from the first question
class Query(graphene.ObjectType):
    all_customers = graphene.List(CustomerType)
    all_products = graphene.List(ProductType)

    def resolve_all_customers(self, info):
        return Customer.objects.all()
    
    def resolve_all_products(self, info):
        return Product.objects.all()

# -- Mutations --
# Customer Mutation
# class CreateCustomer(graphene.Mutation):
#     class Arguments:
#         # Input arguments for the mutation
#         name = graphene.String(required=True)
#         email = graphene.String(required=True)
    
#     # Output fields of the mutation
#     customer = graphene.Field(CustomerType)
#     customer = graphene.String()

#     @staticmethod
#     def mutate(root, info, name, email, phone=None):
#         # Validation
#         if Customer.objects.filter(email=email).exists():
#             raise ValidationError("Email already exists. Please use a different email.")
        
#         if phone:
#             # Simple regex for phone format validation (e.g., +1234567890 or 123-456-7890)
#             if not re.match(r'^(\+?\d{1,3})?[-.\s]?(\d{3})[-.\s]?(\d{3})[-.\s]?(\d{4})$', phone):
#                 raise ValidationError("Invalid phone number format.")
        
#         customer = Customer(name=name, email=email, phone=phone)
#         customer.save()

#         return CreateCustomer(customer=customer, message="Customer created successfully.")
    
# Define a dedicated Input Type for the arguments
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


class CreateCustomer(graphene.Mutation):
    class Arguments:
        # Tell the mutation to expect a single 'input' argument
        print("CreateCustomer mutation called")
        input = CustomerInput(required=True)

    # Define the correct output fields
    customer = graphene.Field(lambda: CustomerType)
    message = graphene.String()

    @staticmethod
    def mutate(root, info, input):
        name = input.get('name')
        email = input.get('email')
        phone = input.get('phone')

        if Customer.objects.filter(email=email).exists():
            raise Exception("Email already exists. Please use a different email.")

        if phone and not re.match(r'^(\+?\d{1,3})?[-.\s]?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}$', phone):
            raise Exception("Invalid phone number format.")

        customer_instance = Customer(name=name, email=email, phone=phone)
        customer_instance.save()

        return CreateCustomer(
            customer=customer_instance,
            message="Customer created successfully."
        )


# Bulk Create Customers Mutation
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(graphene.NonNull(CustomerInput), required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @staticmethod
    @transaction.atomic
    def mutate(root, info, input):
        created_customers = []
        error_messages = []

        # Challenge: Partial success. We process each customer individually.
        for i, customer_data in enumerate(input):
            email = customer_data.get('email')
            phone = customer_data.get('phone')

            # Validation
            if Customer.objects.filter(email=email).exists():
                error_messages.append(f"Record {i+1}: Email '{email}' already exists.")
                continue
            
            if phone and not re.match(r'^(\+?\d{1,3})?[-.\s]?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}$', phone):
                error_messages.append(f"Record {i+1}: Invalid phone number format for '{phone}'.")
                continue

            try:
                customer = Customer.objects.create(
                    name=customer_data.get('name'),
                    email=email,
                    phone=phone
                )
                created_customers.append(customer)
            except Exception as e:
                error_messages.append(f"Record {i+1}: Could not create customer '{customer_data.get('name')}'. Error: {e}")

        return BulkCreateCustomers(customers=created_customers, errors=error_messages)


class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int(default_value=0)

# Create Product Mutation
class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)
    
    product = graphene.Field(ProductType)

    @staticmethod
    def mutate(root, info, input):
        name = input.get('name')
        price = input.get('price')
        stock = input.get('stock')

        print("Price:", price, type(price))
        # Validation
        if price <= 0:
            raise ValidationError("Price must be a positive value.")
        if stock < 0:
            raise ValidationError("Stock cannot be negative.")

        product = Product(name=name, price=Decimal(str(price)), stock=stock)
        product.save()
        return CreateProduct(product=product)


class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.NonNull(graphene.ID), required=True)
    order_date = graphene.DateTime()


# Create Order Mutation
class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)
    
    order = graphene.Field(OrderType)

    @staticmethod
    @transaction.atomic
    def mutate(root, info, input):
        customer_id = input.get('customer_id')
        product_ids = input.get('product_ids')
        order_date = input.get('order_date')

        # Validation
        if not product_ids:
            raise ValidationError("At least one product must be selected for an order.")
            
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            raise ValidationError(f"Invalid customer ID: Customer with ID {customer_id} does not exist.")

        products = Product.objects.filter(pk__in=product_ids)
        if len(products) != len(product_ids):
            found_ids = [str(p.id) for p in products]
            invalid_ids = [pid for pid in product_ids if pid not in found_ids]
            raise ValidationError(f"Invalid product IDs found: {', '.join(invalid_ids)}")

        # Behavior: Calculate total amount
        total_amount = sum(product.price for product in products)
        
        if order_date is None:
            order_date = timezone.now()

        order = Order.objects.create(
            customer=customer,
            total_amount=total_amount,
            order_date=order_date
        )
        
        # Associate products using the ManyToMany relationship
        order.products.set(products)
        
        return CreateOrder(order=order)


# This class groups all the individual mutation classes together.
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
