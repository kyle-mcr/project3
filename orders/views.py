from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.forms import HiddenInput
from .models import MenuItem, OrderItem, Order
from .forms import OrderItemForm

# pylint: disable=no-member

# Create your views here.
def index(request):

    if not request.user.is_authenticated:
        return redirect('login')


    types  = MenuItem.objects.order_by().values_list('type', flat = True).distinct()

    type_dict = {}

    for type in types:
        values = {}

        names = MenuItem.objects.filter(type = type).values_list('name', flat = True).distinct()

        for name in names:
            values[name] = MenuItem.objects.filter(type = type, name = name)

        type_dict[type] = values

    context = {'types' : type_dict}

    return render(request, "index.html", context)

def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    
    if request.method == 'GET':
        return render(request, 'login.html', {"message": None})

    username = request.POST['username']
    password = request.POST['password']

    # Server-side form validation
    if not username:
        return render(request, 'login.html', {"message": "No username."})
    elif len(username) < 4:
        return render(request, 'login.html', {"message": "Username should be longer than 4 characters."})
    elif not password:
        return render(request, 'login.html', {"message": "Type your password."})
    else:
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, 'login.html', {"message": "Login failed."})

def register_view(request):
    if request.method == 'GET':
        return render(request, 'register.html', {"message": None})

    username = request.POST['username']
    email = request.POST['email']
    password = request.POST['password']
    confirmation = request.POST['confirmation']

    # Server-side form validation
    if not username:
        return render(request, 'register.html', {"message": "No username."})
    elif len(username) < 4:
        return render(request, 'register.html', {"message": "Username should be longer than 4 characters."})
    elif not email:
        return render(request, 'register.html', {"message": "No Email."})
    # Email validation required.
    elif not password or not confirmation:
        return render(request, 'register.html', {"message": "Type your password."})
    elif len(password) < 8 or len(confirmation) < 8:
        return render(request, 'register.html', {"message": "Password should be longer than 8 characters."})
    elif password != confirmation:
        return render(request, 'register.html', {"message": "Passwords don't match."})
    elif User.objects.filter(email=email):
        return render(request, 'register.html', {"message": "Email is invalid or already taken."})
    else:
        try:
            User.objects.create_user(username, email, password)
        except:
            return render(request, 'register.html', {"message": "Registration failed."})

    return HttpResponseRedirect(reverse('login'))

def logout_view(request):
    logout(request)
    return render(request, "login.html", {"message": "You're Logged out"})

def add(request, id):
    menuitem = MenuItem.objects.get(pk = id)

    order = Order.objects.filter(user = request.user, status = 'Open').first()

    if order is None:
        order = Order(user = request.user, status = 'Open')
        order.save()

    if request.method == 'POST':
        data = request.POST.copy()
        print(data)
        if 'toppings' in data and data['toppings'] == '':
            del data['toppings']
        if 'extras' in data and data['extras'] == '':
            del data['extras']
        form = OrderItemForm(data)
        print(form.data)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = OrderItemForm(initial = {'menuitem' : menuitem, 'order':order, 'toppings':None})

    form.fields['order'].widget = HiddenInput()
    form.fields['menuitem'].widget = HiddenInput()

    if menuitem.num_toppings == 0:
        form.fields['toppings'].widget = HiddenInput()

    available_items = menuitem.extra_set
    if available_items.count() == 0:
        form.fields['extras'].widget = HiddenInput()
    else:
        form.fields['extras'].queryset = available_items.all()

    context = {'menuitem' : menuitem,
    'form':form}
    return render(request, "add.html", context)


def remove(request, id):
    OrderItem.objects.get(id=id).delete()
    return redirect('cart')


def cancel(request, id):
    order = Order.objects.get(id=id)
    order.status = 'Canceled'
    order.save()
    return redirect('orderlist')


def place(place, id):
    order = Order.objects.get(id=id)
    orderitems_no = order.orderitem_set.count()
    if orderitems_no == 0:
        return redirect('cart')
    order.status = 'Pending'
    order.save()
    return redirect('index')

def cart(request):
    order = Order.objects.filter(user = request.user, status = 'Open').first()

    if order is None:
        order = Order(user = request.user, status = 'Open')
        order.save()

    orderitems = order.orderitem_set.all()
    context = {'order' : order, 'orderitems':orderitems}
    return render(request, "cart.html", context)


def orderlist(request):
    pending_orders = Order.objects.filter(user = request.user, status = 'Pending').all()

    completed_orders = Order.objects.filter(user = request.user, status = 'Completed').all()

    canceled_orders = Order.objects.filter(user = request.user, status = 'Canceled').all()

    context = {'pending_orders' : pending_orders, 'completed_orders' : completed_orders, 'canceled_orders' : canceled_orders}
    return render(request, "orderlist.html", context)