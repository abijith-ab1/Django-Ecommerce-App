from django.contrib.auth import login
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.backends import ModelBackend
from django.http import JsonResponse

from product.models import Product, Category
from .forms import SignUpForm
from .utils import generate_otp, send_otp_email
# Create your views here.
def frontpage(request):
    products = Product.objects.all()[0:8]
    return render(request, 'core/front-page.html', {'products': products})

def signup(request):
    initial_data = {
        'username': request.POST.get('username', ''),
        'first_name': request.POST.get('first_name', ''),
        'last_name': request.POST.get('last_name', ''),
        'email': request.POST.get('email', ''),
    }
    if request.method == 'POST':
        form = SignUpForm(request.POST, initial=initial_data)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']

            # Generate and send OTP
            otp = generate_otp()
            send_otp_email(email, otp)

            # Store OTP in session for verification
            request.session['signup_otp'] = otp

            # Store user data in session temporarily
            request.session['signup_data'] = {
                'username': username,
                'password': password,
                'first_name': first_name,
                'last_name': last_name,
                'email': email
            }
            messages.success(request, 'OTP sent successfully...')
            # Redirect to OTP verification page
            return redirect('otp_verification')
    else:
        form = SignUpForm(initial = initial_data)
    return render(request, 'core/signup.html', {'form': form})

def otp_verification(request):
    if request.method == 'POST':
        otp_entered = request.POST.get('otp', '')
        if 'signup_otp' in request.session:
            otp_stored = request.session['signup_otp']
            if otp_entered == otp_stored:
                # OTP matched, create and save user
                user_data = request.session.get('signup_data')
                user = User.objects.create_user(user_data['username'], email=user_data['email'], password=user_data['password'])
                user.first_name = user_data['first_name']
                user.last_name = user_data['last_name']
                user.save()
                
                # Log in the user
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                
                # Clear session data
                del request.session['signup_otp']
                del request.session['signup_data']
                
                # Redirect to success page or homepage
                return redirect('/')
            else:
                # Invalid OTP, show error message
                messages.error(request, 'Invalid OTP. Please try again...!')
                return render(request, 'core/otp.html')
        else:
            messages.error(request, 'OTP not found. Please sign up again.')
            # OTP not found in session, handle the error
            return render(request, 'core/otp.html', {'error_message': 'OTP not found!'})
    else:
        return render(request, 'core/otp.html')

@login_required(login_url='/login/')
def myaccount(request):
    return render(request, 'core/myaccount.html')

@login_required(login_url='/login/')
def edit_myaccount(request):
    if request.method == "POST":
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.save()
        return redirect('myaccount')
    return render(request, 'core/edit_myaccount.html')

@login_required(login_url='/login/')
def shop(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    active_category = request.GET.get('category', '')

    if active_category:
        products = products.filter(category__slug=active_category)

    query = request.GET.get('query', '')
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    # filter with price
    price_range = request.GET.get('price_range')
    color = request.GET.getlist('color')

    if price_range:
        int_price_range = int(price_range)
        coversion = 100
        total = int_price_range * coversion
        products = products.filter(price__lte=total)

    if color:
        products = products.filter(color__in=color)

    context = {
        "categories": categories,
        "products": products,
        "active_category": active_category
    }
    
    return render(request, 'core/shop.html', context)