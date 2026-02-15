from django.shortcuts import render,get_object_or_404,redirect
from django.http import HttpResponse
from .models import Car,Bid,Watchlist
from django.contrib.auth import authenticate,login,logout
from datetime import datetime
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from .utils import send_brevo_email

from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Q
from .models import Car

from django.utils import timezone

from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Car
from .utils import send_brevo_email

# Create your views here.



from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Car, Bid
from django.utils import timezone

def Home(request):
    now = timezone.now()

    active_cars = Car.objects.filter(
        auction_start__lte=now,
        auction_end__gte=now
    )

    upcoming_cars = Car.objects.filter(
        auction_start__gt=now
    )

    completed_cars = Car.objects.filter(
        auction_end__lt=now
    )

    return render(request, "Home.html", {
        "active_cars": active_cars,
        "upcoming_cars": upcoming_cars,
        "completed_cars": completed_cars,
    })



def bid_car(request, id):

    car = get_object_or_404(Car, id=id)

    if request.method == "POST":

        try:
            amount = int(request.POST.get("amount"))
        except (TypeError, ValueError):
            messages.error(request, "Invalid bid amount.")
            return redirect("car_detail", id=id)

        now = timezone.localtime(timezone.now())
        print("Now:", now)
        print("Start:", car.auction_start)
        print("End:", car.auction_end)
        print("Check:", car.auction_start <= now <= car.auction_end)


        # Check auction time
        if not (car.auction_start <= now <= car.auction_end):
            messages.error(request, "Auction is not active.")
            return redirect("car_detail", id=id)

        # Prevent owner bidding
        if request.user == car.owner:
            messages.error(request, "You cannot bid on your own car.")
            return redirect("car_detail", id=id)

        # Get highest bid
        latest_bid = car.bids.first()

        if latest_bid:
            highest_amount = latest_bid.amount
        else:
            highest_amount = car.base_price

        # Validate bid amount
        if amount <= highest_amount:
            messages.error(request, "Bid must be higher than current highest bid.")
            return redirect("car_detail", id=id)

        # Create bid
      

        Bid.objects.create(
            car=car,
            bidder=request.user,
            amount=amount
        )

        messages.success(request, "Your bid was placed successfully!")
        return redirect("car_detail", id=id)

    return redirect("car_detail", id=id)

def register_view(request):

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("pass2")

        # Password match check
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        # Username exists check
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")

        # Email exists check
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("register")

        # Create user
        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "Account created successfully. Please login.")
        return redirect("login_view")

    return render(request, "Register.html")
def login_view(request):

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login_view")

    return render(request, "Login.html")
def logout_view(request):
    logout(request)
    return redirect("login_view")



def Car_list(request):
    now = timezone.now()

    # 🔥 Base queryset → only active auctions
    cars = Car.objects.filter(
        auction_start__lte=now,
        auction_end__gte=now
    )

    # ==========================
    # 🔎 SEARCH
    # ==========================
    search_query = request.GET.get("search")
    if search_query:
        cars = cars.filter(
            Q(title__icontains=search_query) |
            Q(brand__icontains=search_query)
        )

    # ==========================
    # 🚗 FILTER BY VEHICLE TYPE
    # ==========================
    vehicle_type = request.GET.get("type")
    if vehicle_type in ["2", "4"]:
        cars = cars.filter(type=vehicle_type)

    # ==========================
    # 💰 SORT BY BASE PRICE
    # ==========================
    sort = request.GET.get("sort")

    if sort == "low":
        cars = cars.order_by("base_price")

    elif sort == "high":
        cars = cars.order_by("-base_price")

    else:
        # Default sorting (latest created)
        cars = cars.order_by("-created_at")

    context = {
        "cars": cars,
    }

    return render(request, "Car_list.html", context)

def car_detail(request, id):
    car = get_object_or_404(Car, id=id)
    now = timezone.now()

    if now > car.auction_end and car.status != "Completed":

        highest_bid = car.bids.order_by('-amount').first()

        if highest_bid:
            car.winner = highest_bid.bidder

        car.status = "Completed"
        car.save()

        if highest_bid and highest_bid.bidder.email:

            subject = "🎉 You Won the Auction!"

            message = f"""
Congratulations {highest_bid.bidder.username}!

You have successfully won the auction for:

Car: {car.title}
Winning Bid: ₹{highest_bid.amount}

Please contact the seller to proceed further.

Thank you for using Auction.IN 🚗
"""

            send_brevo_email(
                highest_bid.bidder.email,
                subject,
                message
            )

    all_bid = car.bids.order_by('-created_at')
    highest_bid = car.bids.order_by('-amount').first()
    total_bids = car.bids.count()

    context = {
        "car": car,
        "highest_bid": highest_bid,
        "total_bids": total_bids,
        "all_bid": all_bid,
    }

    return render(request, "car_detail.html", context)



@login_required
def add_car(request):
    

    if request.method == "POST":
        Car.objects.create(
            title=request.POST.get("title"),
            brand=request.POST.get("brand"),
            model_name=request.POST.get("model_name"),
            year=request.POST.get("year"),
            description=request.POST.get("description"),
            base_price=request.POST.get("base_price"),
            auction_start=request.POST.get("auction_start"),
            auction_end=request.POST.get("auction_end"),
            type=request.POST.get('vehicle_type'),
            image=request.FILES.get("image"),

            owner=request.user
        )
        messages.success(request, "Car added successfully!")
        return redirect("car_list")

    return render(request, "add_car.html")




@login_required
def my_bidding(request):
    user = request.user

    # Cars user has placed bids on
    bid_cars = Car.objects.filter(bids__bidder=user).distinct()

    # Cars user won
    won_cars = Car.objects.filter(winner=user)

    context = {
        "bid_cars": bid_cars,
        "won_cars": won_cars,
    }

    return render(request, "my_bidding.html", context)
@login_required
def my_listings(request):
    uploaded_cars = Car.objects.filter(owner=request.user)

    return render(request, "my_listings.html", {
        "uploaded_cars": uploaded_cars
    })


from .utils import predict_vehicle_price

def Find_price(request):
    predicted_price = None

    if request.method == "POST":
        data = {
            "vehicle_type": request.POST.get("vehicle_type"),  # 2 or 4
            "brand": request.POST.get("brand"),
            "model": request.POST.get("Model"),
            "year": request.POST.get("year"),
            "km_driven": request.POST.get("km_driven"),
            "fuel": request.POST.get("fuel"),
            "condition": request.POST.get("condition"),
        }

        predicted_price = predict_vehicle_price(data)
        print(predicted_price)

    return render(request, 'AI.html', {"price": predicted_price})
