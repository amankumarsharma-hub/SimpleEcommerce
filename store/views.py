from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Order,Category
from django.contrib.auth.decorators import login_required
from .models import Wishlist
import razorpay
from django.conf import settings
from django.core.mail import send_mail
from .models import Review
from django.db.models import Avg
from .models import OrderItem
from django.db.models import Sum
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator

from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

@staff_member_required
def admin_dashboard(request):


    total_products = Product.objects.count()

    total_users = User.objects.count()

    total_orders = Order.objects.count()

    revenue = Order.objects.aggregate(
        Sum("total_amount")
    )["total_amount__sum"] or 0

    orders = Order.objects.order_by("created_at")

    labels = []
    amounts = []

    for order in orders:
        labels.append(order.created_at.strftime("%d %b"))
        amounts.append(float(order.total_amount))

    context = {
        "total_products": total_products,
        "total_users": total_users,
        "total_orders": total_orders,
        "revenue": revenue,
        "labels": labels,
        "amounts": amounts,
    }

    return render(request, "admin_dashboard.html", context)


def home(request):

    category_id = request.GET.get("category")
    search = request.GET.get("search")
    sort = request.GET.get("sort")

    categories = Category.objects.all()

    products = Product.objects.all()

    if category_id:
        products = products.filter(category_id=category_id)

    if search:
        products = products.filter(name__icontains=search)

    if sort == "low":
        products = products.order_by("price")

    elif sort == "high":
        products = products.order_by("-price")

    elif sort == "az":
        products = products.order_by("name")

    elif sort == "za":
        products = products.order_by("-name")

    elif sort == "new":
        products = products.order_by("-id")

    # Pagination hamesha chalegi
    paginator = Paginator(products, 6)

    page_number = request.GET.get("page")
    featured_products = Product.objects.filter(featured=True)[:4]

    page_obj = paginator.get_page(page_number)

    return render(request, "home.html", {
        "products": page_obj,
        "page_obj": page_obj,
        "categories": categories,
        "selected_category": category_id,
        "search": search,
        "sort": sort,
        "featured_products": featured_products,
    })    
    
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})

    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1

    request.session['cart'] = cart

    return redirect('home')

def cart(request):

    cart = request.session.get('cart', {})

    products = []

    total = 0

    for product_id, quantity in cart.items():

        product = Product.objects.get(id=product_id)

        product.quantity = quantity

        product.subtotal = product.price * quantity

        total += product.subtotal

        products.append(product)

    return render(request, "cart.html", {
        "products": products,
        "total": total
    })    

def checkout(request):
    cart = request.session.get("cart", {})
    products = []
    total = 0

    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        product.quantity = quantity
        product.subtotal = product.price * quantity
        total += product.subtotal
        products.append(product)

    if request.method == "POST":

        customer_name = request.POST["name"]
        email = request.POST["email"]
        address = request.POST["address"]

        # Create Order
        order = Order.objects.create(
            user=request.user,
            customer_name=customer_name,
            email=email,
            address=address,
            total_amount=total
        )

        # Save all products in OrderItem
        for product in products:
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=product.quantity,
                price=product.price
            )

#         # Send Email
#         send_mail(
#             subject="Order Confirmation - Simple E-Commerce",
#             message=f"""
# Hello {customer_name},

# Thank you for shopping with us!

# Your order has been placed successfully.

# Total Amount: ₹{total}

# Your order will be delivered soon.

# Regards,
# Simple E-Commerce Team
# """,
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             recipient_list=[email],
#             fail_silently=False,
#         )

        request.session["cart"] = {}

        return render(request, "success.html")

    return render(request, "checkout.html", {
        "products": products,
        "total": total
    })

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})

    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]

    request.session['cart'] = cart

    return redirect('cart')    

def increase_quantity(request, product_id):
    cart = request.session.get('cart', {})

    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] += 1

    request.session['cart'] = cart

    return redirect('cart')


def decrease_quantity(request, product_id):
    cart = request.session.get('cart', {})

    product_id = str(product_id)

    if product_id in cart:
        if cart[product_id] > 1:
            cart[product_id] -= 1
        else:
            del cart[product_id]

    request.session['cart'] = cart

    return redirect('cart')   

def product_detail(request, id):

    product = get_object_or_404(Product, id=id)

    reviews = Review.objects.filter(product=product).order_by("-created_at")

    average_rating = reviews.aggregate(Avg("rating"))["rating__avg"]

    review_count = reviews.count()

    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]

    # Similar Products
    similar_products = Product.objects.filter(
        category=product.category
    ).exclude(
        id=product.id
    )[:4]

    if request.method == "POST":

        if request.user.is_authenticated:

            Review.objects.create(
                product=product,
                user=request.user,
                rating=request.POST["rating"],
                comment=request.POST["comment"]
            )

            return redirect("product_detail", id=product.id)

        return redirect("login")

    return render(request, "product_detail.html", {
        "product": product,
        "reviews": reviews,
        "average_rating": average_rating,
        "review_count": review_count,
        "similar_products": similar_products,
        "related_products": related_products,
    })
@login_required
def add_to_wishlist(request, id):

    product = get_object_or_404(Product, id=id)

    Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    return redirect("wishlist")

@login_required
def wishlist(request):

    items = Wishlist.objects.filter(user=request.user)

    return render(request, "wishlist.html", {
        "items": items
    })        

@login_required
def my_orders(request):

    orders = Order.objects.filter(
        user=request.user
    ).order_by("-id")

    return render(request, "my_orders.html", {
        "orders": orders
    })    



def payment(request):

    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        )
    )

    # ₹500 = 50000 paise
    amount = 50000

    payment = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": "1"
    })

    context = {
        "payment": payment,
        "key": settings.RAZORPAY_KEY_ID
    }

    return render(request, "payment.html", context)    

def payment_success(request):
    return render(request, "payment_success.html")


def payment_failed(request):

    return render(request, "payment_failed.html")    


def download_invoice(request, order_id):

    order = Order.objects.get(id=order_id)

    response = HttpResponse(content_type="application/pdf")

    response["Content-Disposition"] = (
        f'attachment; filename="Invoice_{order.id}.pdf"'
    )

    doc = SimpleDocTemplate(response)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph("<b>Simple E-Commerce Invoice</b>", styles["Title"])
    )

    elements.append(
        Paragraph(f"Order ID: {order.id}", styles["Normal"])
    )

    elements.append(
        Paragraph(f"Customer: {order.customer_name}", styles["Normal"])
    )

    elements.append(
        Paragraph(f"Email: {order.email}", styles["Normal"])
    )

    elements.append(
        Paragraph(f"Address: {order.address}", styles["Normal"])
    )

    elements.append(
        Paragraph("<br/>", styles["Normal"])
    )

    data = [
        ["Product", "Qty", "Price"]
    ]

    for item in order.items.all():

        data.append([
            item.product.name,
            str(item.quantity),
            f"₹{item.price}"
        ])

    table = Table(data)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("BOTTOMPADDING", (0,0), (-1,0), 10),
    ]))

    elements.append(table)

    elements.append(
        Paragraph(
            f"<br/><b>Total Amount : ₹{order.total_amount}</b>",
            styles["Heading2"]
        )
    )

    doc.build(elements)

    return response