from django.shortcuts import render

from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import CategoryForm, ProductForm
from .models import Products,Cart,Category,Order,Payment
from django.contrib import messages


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password ==password2:
            if User.objects.filter(username=username, password=password):
                return({'error':'username already exists'})
                # messages.error(request"&&&&")
            else:
                user = User.objects.create_user(username=username, password=password)
                user.save()
                return redirect('login')
                # messages.success(request,"yyyyyy")
        # else:
            # messages.error(request,"&y&y")
    return render(request, 'register.html')

def login_view(request):
    if request.method =='POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate (request, username=username, password=password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            return render(request,'login.html',{'error':'invalid credentials'})
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def services(request):
    return render(request, 'services.html')

def contact(request):
    return render(request, 'contact.html')


@login_required
def create_category(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            form = CategoryForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('create_product')
        else:
            form = CategoryForm()
            return render(request, 'create_category.html', {'form':form})
    else:
        return redirect('home')

def create_product(request):
    if request.method =='POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
        return render(request, 'create_product.html', {'form': form})

def product_list(request):
    products = Products.objects.all()
    return render(request, 'product_list.html', {'products':products})

def add_cart(request,product_id):
    try:
        product=Products.objects.get(id=product_id)
    except Products.DoesNotExist:
        return redirect('product_list')
    if product.stock>0:
        if Cart.objects.filter(product=product,user=request.user).exists():
            cart=Cart.objects.get(product=product,user=request.user)
            cart.quantity+=1
        else:
            cart=Cart.objects.create(product=product,user=request.user)
        cart.save()  
        product.stock-=1
        product.save()
    return redirect('cart_view')

def cart_view(request):
    carts=Cart.objects.filter(user=request.user)
    total=0
    for cart in carts:
        total+=cart.product.price*cart.quantity
    return render(request, 'cart.html',{'carts':carts,'total':total})

def remove_cart(request,cart_id):
    cart=Cart.objects.get(id=cart_id, user=request.user)
    cart.product.stock += cart.quantity
    cart.product.save()
    cart.delete()
    cart.product.stock+=1
    cart.product.save()
    return redirect('cart_view')

@login_required
def remove_all_cart(request):
    cart = Cart.objects.filter(user=request.user)
    for carts in cart:
        carts.product.stock += carts.quantity
        carts.product.save()

    cart.delete()

    return redirect('cart_view')


def Category_list(request):
    categories=Category.objects.all()
    selected_category_id= request.GET.get('category_id')
    products = Products.objects.filter(category_id=selected_category_id) if selected_category_id else Products.objects.all()
    return render(request, 'category_list.html', {'categories':categories, 'products':products, 'selected_category_id':selected_category_id})

@login_required
def update_product(request, id):
    product=Products.objects.get(id=id)
    if request.user.is_superuser:
        if request.method =='POST':
            form = ProductForm(request.POST, request.FILES, instance=product)
            if form.is_valid:
                form.save()
                return redirect('product_list')
        else:
            form = ProductForm(instance=product)
            return render (request, 'update_product.html', {'form':form})
    else:
        return redirect('home')
    
@login_required
def delete_product(request,id):
    product = Products.objects.get(id=id)
    if request.user.is_superuser:
        product.delete()
        return redirect('product_list')
    else:
        return redirect ('home')
    

@login_required
def increment_quantity(request, cart_id):
    cart = Cart.objects.filter(id=cart_id, user=request.user).first()

    if cart.product.stock > 0:
        cart.quantity += 1
        cart.product.stock -= 1
        cart.save()
        cart.product.save()
    
    return redirect('cart_view')

@login_required
def decrement_quantity(request, cart_id):
    cart = Cart.objects.filter(id =cart_id, user =request.user).first()

    if cart.product.stock > 1:
        cart.quantity -=1
        cart.product.stock +=1
        cart.save()
        cart.product.save()
    else:
        cart.product.stock += cart.quantity
        cart.product.save()
        cart.delete()


    return redirect('cart_view')


@login_required
def place_order(request):
    carts = Cart.objects.filter(user=request.user)
    if not carts.exists():
        return redirect('cart')
    
    total_price = sum(cart.product.price * cart.quantity for cart in carts)
    
    order = Order.objects.create(
        user = request.user, total_price = total_price 
    )

    carts.delete

    return redirect('payment', order_id = order.id)

@login_required
def payment(request, order_id):
    order = Order.objects.get(id = order_id, user = request.user)

    if request.method == 'POST':
        payment_method = request.POST['payment_method']

        Payment.objects.create(
            order = order,
            payment_method = payment_method,
            status = 'completed' if payment_method == 'online' else 'pending'

        )

        order.status = 'processing'
        order.save()

        return redirect('success')
    
    return render(request, 'payment.html', {'order' : order})

def success(request):
    return render(request, 'success.html')

@login_required
def order_history(request):
    order = Order.objects.filter(user = request.user).order_by('-created_at')
    return render (request, 'order_history.html',{'orders':order})

@login_required

def update_order_status(request, order_id):
    order = Order.objects.get(id=order_id)
    payment = Payment.objects.get(order=order)

    if request.user.is_superuser:
        if request.method == 'POST':
            new_status = request.POST.get('status')
            new_payment_status = request.POST.get('payment_status')


            if new_status in dict(Order.STATUS_CHOICES):
                order.status = new_status
                order.save()


            if payment.payment_method == 'COD' and new_payment_status in dict(Payment.PAYMENT_STATUS_CHOICE):
                payment.status = new_payment_status
                order.save()

            messages.success(request, "Order and payment status updated successfully")
        return redirect('all_orders')
    messages.error(request,'you do not have permission to update the orders')
    return redirect('all_orders')


@login_required
def all_orders(request):
    if request.user.is_superuser:
        order = Order.objects.all().order_by('-created_at')
        return render(request, 'admin_orders.html', {'order':order})
    else:
        return redirect('home')
