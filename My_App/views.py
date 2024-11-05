from datetime import datetime
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render,HttpResponse,redirect
from My_App.models import *
from django.db.models import Q
import  razorpay




def home(request):
    products = ProductTable.objects.all()
    return render(request, 'PRS/home.html',{'products':products})

def login(request):
    return render(request, 'PRS/login.html')

def user_logout(request):
    del request.session['lid']
    return redirect('/')

def admin_logout(request):
    del request.session['lid']
    return redirect('/')

def seller_logout(request):
    del request.session['lid']
    return redirect('/')

def login_post(request):
    username = request.POST['username']
    password = request.POST['password']

    login_fetch = LoginTable.objects.filter(username=username,password=password)
    if login_fetch.exists():
        login_get = LoginTable.objects.get(username=username,password=password)
        request.session['lid'] = login_get.id

        if login_get.type == 'admin':
            return redirect('/admin_home')

        elif login_get.type == 'seller':
            seller = SellerTable.objects.get(LOGIN_ID_id=request.session['lid'])
            request.session['sellername'] = seller.name
            return redirect('/seller_home')

        elif login_get.type == 'user':
            user = UserTable.objects.get(LOGIN_ID_id=request.session['lid'])
            request.session['username'] = user.name
            return redirect('/user_home')

        elif login_get.type == 'pending':
            return HttpResponse('''<script>window.location='/';</script>''')
        elif login_get.type == 'blocked':
            return HttpResponse('''<script>alert window.location='/';</script>''')
        else:
            return HttpResponse('''<script>window.location='/';</script>''')
    else:
        return HttpResponse('''<script>window.location='/';</script>''')


def user_registration(request):
    if request.method == "POST":
        name = request.POST['name']
        gender = request.POST['gender']
        place = request.POST['place']
        pin = request.POST['pin']
        post = request.POST['post']
        phone = request.POST['phone']
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        image = request.FILES['image']

        if LoginTable.objects.filter(username=username,password=password).exists():
            return HttpResponse('''<script>alert("Username already exists. Cannot create account."); window.location='user_registration';</script>''')

        user_login_details = LoginTable.objects.create(
            username=username,
            password=password,
            type='user'
        )
        user_login_details.save()

        fs = FileSystemStorage()
        date = datetime.now().strftime("%Y-%m-%d")
        fs.save(date,image)
        path = date

        user_profile_details = UserTable.objects.create(
            LOGIN_ID=user_login_details,
            name=name,
            gender=gender,
            place=place,
            pin=pin,
            post=post,
            phone=phone,
            email=email,
            image=path
        )
        user_profile_details.save()
        return HttpResponse('''<script> window.location='/';</script>''')
    return render(request, 'User/registration.html')


def seller_registration(request):
    if request.method == "POST":
        name = request.POST['name']
        place = request.POST['place']
        phone = request.POST['phone']
        email = request.POST['email']
        image = request.FILES['image']
        id_proof = request.FILES['id_proof']
        username = request.POST['username']
        password = request.POST['password']

        if LoginTable.objects.filter(username=username,password=password).exists():
            return HttpResponse('''<script>alert("Username already exists. Cannot create account."); window.location='/seller_registration';</script>''')


        seller_login_details = LoginTable.objects.create(
            username=username,
            password=password,
            type='pending'
        )
        seller_login_details.save()

        fs = FileSystemStorage()
        fp = fs.save(image.name, image)
        fpid = fs.save(id_proof.name,id_proof)

        seller_profile_details = SellerTable.objects.create(
            LOGIN_ID = seller_login_details,
            name=name,
            place=place,
            phone=phone,
            email=email,
            image=fp,
            id_proof=fpid
        )
        seller_profile_details.save()
        return HttpResponse('''<script>  window.location='/';</script>''')
    return render(request, 'Seller/registration.html')

def admin_home(request):
    return render(request, 'Admin/home.html')

def verify_seller(request):
    sellers = SellerTable.objects.all()
    return render(request, 'Admin/verify_seller.html',{'sellers':sellers})


from django.db.models import Avg


def verify_seller_product_rate(request, sellerid):
    seller = SellerTable.objects.get(id=sellerid)

    products = ProductTable.objects.filter(SELLER_ID=seller)

    # Initialize a list to hold product ratings and feedback
    product_feedbacks = []

    for product in products:
        feedbacks = FeedbackTable.objects.filter(ORDERDETAILS__PRODUCT_ID=product)
        ratings = [int(feedback.ratings) for feedback in feedbacks]

        # Calculate average rating
        average_rating = sum(ratings) / len(ratings) if ratings else 0

        product_feedbacks.append({
            'product_name': product.product_name,
            'average_rating': average_rating,
            'feedbacks': feedbacks,
        })

    return render(request, 'Admin/View_product_rating.html', {
        'seller': seller,
        'product_feedbacks': product_feedbacks,
    })


def product_feedback(request,pid):
    ob=FeedbackTable.objects.filter(PRODUCT=pid)
    return render(request, 'Admin/View_feedback.html',{'sellers':ob})


def product_feedbackadmin(request):
    feedbacks = FeedbackTable.objects.filter(
        ORDERDETAILS__PRODUCT_ID__SELLER_ID__LOGIN_ID__id=request.session['lid']
    ).select_related('ORDERDETAILS__PRODUCT_ID').order_by('-id')

    return render(request, 'Seller/sel_View_feedback.html', {'feedbacks': feedbacks})




def accept_reject_seller(request):
    login_id = request.POST['login_id']
    action = request.POST['action']

    login = LoginTable.objects.get(id=login_id)

    if action == "accept":
        login.type = "seller"
    elif action == "reject":
        login.type = "pending"
    login.save()
    return redirect('/verify_seller')


def block_unblock_seller(request):
    login_id = request.POST['login_id']
    action = request.POST['action']

    login = LoginTable.objects.get(id=login_id)

    if action == "block":
        login.type = "blocked"
    elif action == "unblock":
        login.type = "seller"
    login.save()
    return HttpResponse(f'''<script> window.location='/verify_seller';</script>''')


def admin_view_users(request):
    users = UserTable.objects.all()
    return render(request, 'Admin/view_users.html',{'users':users})

def user_profile(request):
    profile = UserTable.objects.get(LOGIN_ID_id=request.session['lid'])
    return render(request, 'User/view_profile.html',{'profile':profile})

def edit_profile(request):
    profile = UserTable.objects.get(LOGIN_ID_id=request.session['lid'])
    return render(request, 'User/edit_profile.html',{'profile':profile})

def edit_profile_post(request):
    id = request.POST['id']
    name = request.POST['name']
    gender = request.POST['gender']
    place = request.POST['place']
    pin = request.POST['pin']
    post = request.POST['post']
    phone = request.POST['phone']
    email = request.POST['email']

    user = UserTable.objects.get(id=id)

    if 'image' in request.FILES:
        image = request.FILES['image']
        fs = FileSystemStorage()
        fp = fs.save(image.name,image)
        user.image = fp


    user.name=name
    user.gender=gender
    user.place=place
    user.pin=pin
    user.post=post
    user.phone=phone
    user.email=email
    user.save()
    return redirect('/user_profile')

#------------------------------------------------------------Seller Home----------------------------------------------------------------
def seller_home(request):
    try:
        mlist = []
        shipping = OrderDetails.objects.filter(PRODUCT_ID__SELLER_ID__LOGIN_ID=request.session['lid'], status='accepted').order_by('-id')

        for i in range(1, 13):
            ob = OrderDetails.objects.filter(PRODUCT_ID__SELLER_ID__LOGIN_ID=request.session['lid'], ORDER_ID__date__month=i)
            tp = 0
            for order in ob:
                tp += order.quantity * order.PRODUCT_ID.price
            mlist.append(tp)

        # Count the statuses of orders
        requested_count = OrderDetails.objects.filter(PRODUCT_ID__SELLER_ID__LOGIN_ID=request.session['lid'], status='cart').count()
        accepted_count = OrderDetails.objects.filter(PRODUCT_ID__SELLER_ID__LOGIN_ID=request.session['lid'], status='accepted').count()
        rejected_count = OrderDetails.objects.filter(PRODUCT_ID__SELLER_ID__LOGIN_ID=request.session['lid'], status='rejected').count()

        return render(request, 'Seller/home.html', {
            "ml": mlist,
            'shipping': shipping,
            'requested_count': requested_count,
            'accepted_count': accepted_count,
            'rejected_count': rejected_count
        })


    except Exception as e:
        print(e)



def seller_view_profile(request):
    seller_profile = SellerTable.objects.get(LOGIN_ID_id=request.session['lid'])
    return render(request, 'Seller/view_profile.html',{'seller_profile':seller_profile})

def seller_edit_profile(request):
    seller = SellerTable.objects.get(LOGIN_ID_id=request.session['lid'])
    return render(request, 'Seller/edit_profile.html',{'seller':seller})

def seller_edit_profile_post(request):
    id = request.POST['id']
    name = request.POST['name']
    place = request.POST['place']
    phone = request.POST['phone']
    email = request.POST['email']

    seller = SellerTable.objects.get(id=id)
    seller.name=name
    seller.place=place
    seller.phone=phone
    seller.email=email

    if 'image' in request.FILES:
        image = request.FILES['image']
        fs = FileSystemStorage()
        fp = fs.save(image.name, image)
        seller.image = fp
    if 'id_proof' in request.FILES:
        idproof = request.FILES['sellerid']
        fs1 = FileSystemStorage()
        fp1 = fs1.save(idproof.name, idproof)
        seller.id_proof = fp1
    seller.save()
    return redirect('/seller_view_profile')

def seller_manage_products(request):
    products = ProductTable.objects.filter(SELLER_ID__LOGIN_ID_id=request.session['lid'])
    return render(request, 'Seller/view_products.html',{'products':products})

def seller_add_product(request):
    if request.method =='POST':
        id = request.session['lid']
        product_name = request.POST['product_name']
        price = request.POST['price']
        stock = request.POST['stock']
        image = request.FILES['image']

        seller = SellerTable.objects.get(LOGIN_ID_id=id)

        fs =FileSystemStorage()
        fp = fs.save(image.name,image)

        products = ProductTable(
            SELLER_ID=seller,
            product_name=product_name,
            price=price,
            stock=stock,
            Date=datetime.today(),
            image=fp
        )
        products.save()
        return redirect('/seller_manage_products')
    return render(request, 'Seller/add_product.html')

def edit_product(request,id):
    product = ProductTable.objects.get(id=id)
    return render(request, 'Seller/edit_product.html',{'product':product})

def edit_product_post(request):
    product_name = request.POST['product_name']
    id = request.POST['id']
    price = request.POST['price']
    stock = request.POST['stock']

    products = ProductTable.objects.get(id=id)
    products.product_name = product_name
    products.price = price
    products.stock = stock


    if 'image' in request.FILES:
        image = request.FILES['image']
        fs = FileSystemStorage()
        fp = fs.save(image.name,image)
        products.image = fp
        products.save()
    products.save()
    return redirect('/seller_manage_products')

def delete_product(request,id):
    product = ProductTable.objects.get(id=id)
    product.delete()
    return redirect('/seller_manage_products')


def verify_orders(request):
    seller_id = SellerTable.objects.get(LOGIN_ID_id=request.session['lid'])
    orders = OrderDetails.objects.filter(PRODUCT_ID__SELLER_ID_id=seller_id,status='cart')
    # orders = OrderDetails.objects.filter(PRODUCT_ID__SELLER_ID_id=seller_id)
    odids=[]
    for i in orders:
        odids.append(i.ORDER_ID.id)
    orders=OrderTable.objects.filter(id__in=odids,status='requested')
    # orders=OrderTable.objects.filter(id__in=odids)
    for i in orders:
        od=OrderDetails.objects.filter(PRODUCT_ID__SELLER_ID_id=seller_id,ORDER_ID=i)
        tm=0
        for j in od:
            tm+=j.price
        i.tm=tm
    return render(request, 'Seller/verify_orders.html', {'orders':orders})

def view_more_order(request, id):
    seller_id = SellerTable.objects.get(LOGIN_ID_id=request.session['lid'])
    order = OrderTable.objects.get(id=id)

    order_details = OrderDetails.objects.filter(ORDER_ID=order,PRODUCT_ID__SELLER_ID=seller_id)

    total_amount = sum(detail.price for detail in order_details)

    return render(request, 'Seller/view_more_order.html', {
        'order_details': order_details,
        'total_amount': total_amount,
        'order': order
    })

def accept_order(request,id):
    seller_id = SellerTable.objects.get(LOGIN_ID_id=request.session['lid'])
    order = OrderTable.objects.get(id=id)
    if OrderDetails.objects.filter(ORDER_ID=order, PRODUCT_ID__SELLER_ID=seller_id).exists():
        order_details = OrderDetails.objects.filter(ORDER_ID=order,PRODUCT_ID__SELLER_ID=seller_id)
        for order_detail in order_details:
            order_detail.status = 'accepted'
            order_detail.save()
    else:
        return ('/verify_seller')
    return redirect('/verify_orders')



def reject_order(request,id):
    seller_id = SellerTable.objects.get(LOGIN_ID_id=request.session['lid'])
    order = OrderTable.objects.get(id=id)
    if OrderDetails.objects.filter(ORDER_ID=order, PRODUCT_ID__SELLER_ID=seller_id).exists():
        order_details = OrderDetails.objects.filter(ORDER_ID=order,PRODUCT_ID__SELLER_ID=seller_id)
        for order_detail in order_details:
            order_detail.status = 'rejected'
            order_detail.save()
    else:
        return HttpResponse("/Permission Denied")
    return redirect('/verify_orders')


def seller_view_order_history(request):
    seller = SellerTable.objects.get(LOGIN_ID=request.session['lid'])
    orders = OrderDetails.objects.filter(PRODUCT_ID__SELLER_ID=seller)
    return render(request, 'Seller/view_order_history.html',{'orders':orders})























def user_home(request):
    products = ProductTable.objects.all().order_by('-id')
    return render(request, 'User/user_home.html',{'products':products})

def user_view_complaint(request):
    id = request.session['lid']
    complaints = ComplaintTable.objects.filter(USER_ID__LOGIN_ID_id=id)
    return render(request, 'User/view_compaints.html',{'complaints':complaints})


def add_new(request):
    if request.method == 'POST':
        id = request.session['lid']
        complaint = request.POST['complaint']

        user = UserTable.objects.get(LOGIN_ID_id=id)

        complaint_data = ComplaintTable(
            USER_ID=user,
            complaint=complaint,
            reply='pending'
        )
        complaint_data.save()
        return redirect('/user_view_complaint')
    return render(request, 'User/send_complaint.html')

def advim_view_complaint(request):
    complaints = ComplaintTable.objects.all()
    return render(request, 'Admin/view_complaint.html',{'complaints':complaints})

def complaint_reply(request,id):
    complaint = ComplaintTable.objects.get(id=id)
    request.session['cid']=id
    return render(request, 'Admin/send_reply.html',{'complaint':complaint})

def complaint_reply_post(request):
    reply=request.POST['reply']
    id = request.POST['id']

    complaint = ComplaintTable.objects.get(id=id)
    complaint.reply = reply
    complaint.save()
    return redirect('/advim_view_complaint')

def view_all_products(request):
    products = ProductTable.objects.all().order_by('-stock')
    return render(request, 'User/view_products.html',{'products':products})

def add_rating(request):
    product_id=request.POST['book_id']
    ratings=request.POST['rating']
    feedback=request.POST["feedback"]
    c=FeedbackTable()
    c.feedback = feedback
    c.ratings=ratings
    c.PRODUCT=ProductTable.objects.get(id=product_id)
    c.USER_ID=UserTable.objects.get(LOGIN_ID=request.session["lid"])
    c.save()
    return redirect("/view_all_products")

def search_products(request):
    query = request.GET.get('query', '')
    if query!="":
        # try:
        #     ob=UserHistoryTable.objects.get(USER_ID__LOGIN_ID__id=request.session['lid'])
        #     ob.Keyword=query
        #     ob.date=datetime.today()
        #     ob.save()
        # except:
        ob = UserHistoryTable()
        ob.USER_ID=UserTable.objects.get(LOGIN_ID__id=request.session['lid'])
        ob.Keyword = query
        ob.date = datetime.today()
        ob.save()
    if query:
        products = ProductTable.objects.filter(product_name__icontains=query)
    else:
        products = ProductTable.objects.all()
    return render(request, 'User/view_products.html', {'products': products})

def add_to_cart(request,id):
    user = UserTable.objects.get(LOGIN_ID_id=request.session['lid'])
    product = ProductTable.objects.get(id=id)
    if product.stock>0:
        order = OrderTable.objects.filter(USER_ID_id=user,status='cart')
        if len(order)==0:
            order=OrderTable()
            order. USER_ID =user
            order.date = datetime.today()
            order.amount = 0
            order.status ='cart'
            order.save()
        else:
            order=order[0]

        ob=OrderDetails.objects.filter(ORDER_ID__id =order.id,PRODUCT_ID__id =id)
        if len(ob)==0:
            ob=OrderDetails()
            ob.ORDER_ID = order
            ob.PRODUCT_ID = product
            ob.quantity = 1
            ob.price = product.price
            ob.status ='cart'
            ob.save()
        else:
            ob = ob[0]
            ob.quantity += 1
            ob.price = ob.quantity * product.price
            ob.save()
        order.amount += product.price
        order.save()
        # product.stock -= 1
        # product.save()
    else:
        return HttpResponse('''<script>alert("Out Of Stock"); window.location='/view_all_products';</script>''')
    return HttpResponse(''' 
                            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/sweetalert2@10">
                            <script src="https://cdn.jsdelivr.net/npm/sweetalert2@10"></script>
                            <script>
                                document.addEventListener("DOMContentLoaded", function() {
                                    Swal.fire({
                                        icon: 'success',
                                        title: 'Added to Cart',
                                        text: 'Product successfully added to cart',
                                        confirmButtonText: 'OK',
                                        reverseButtons: true
                                    }).then((result) => {
                                        if (result.isConfirmed) {
                                            window.history.back();  
                                        }
                                    });
                                });
                            </script>
                        ''')

def view_cart(request):
    user = UserTable.objects.get(LOGIN_ID=request.session['lid'])
    order = OrderTable.objects.filter(USER_ID_id=user, status='cart').first()

    if order:
        order_details = OrderDetails.objects.filter(ORDER_ID=order)
        total_amount = sum(item.price for item in order_details)
        gst = total_amount * 12 / 100
        total = total_amount + gst
        num = order_details.count()
    else:
        order_details = []
        total_amount = 0
        gst = 0
        total = 0
        num = 0

    return render(request, 'User/user_view_cart.html', {
        'order_details': order_details,
        'total_amount': total_amount,
        'total': total,
        'gst': gst,
        'num': num,
        'order': order
    })

def remove_from_cart(request,id):
    user = UserTable.objects.get(LOGIN_ID_id=request.session['lid'])
    order = OrderTable.objects.filter(USER_ID=user,status='cart').first()
    product = OrderDetails.objects.filter(ORDER_ID=order, PRODUCT_ID_id=id).first()
    product.delete()
    order.delete()
    return redirect('/view_cart')




def send_request(request,id):
    user = UserTable.objects.get(LOGIN_ID_id=request.session['lid'])
    order = OrderTable.objects.get(id=id,USER_ID=user,status='cart')

    order_details = OrderDetails.objects.filter(ORDER_ID=order)
    total_amount = sum(item.price for item in order_details)
    gst = total_amount * 12 / 100
    total = total_amount + gst

    order.status = 'requested'
    order.amount = total
    order.save()

    return HttpResponse(''' 
                                <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/sweetalert2@10">
                                <script src="https://cdn.jsdelivr.net/npm/sweetalert2@10"></script>
                                <script>
                                    document.addEventListener("DOMContentLoaded", function() {
                                        Swal.fire({
                                            icon: 'success',
                                            title: 'Request send successfully',
                                            text: 'Requested',
                                            confirmButtonText: 'OK',
                                            reverseButtons: true
                                        }).then((result) => {
                                            if (result.isConfirmed) {
                                                window.history.back();  
                                            }
                                        });
                                    });
                                </script>
                            ''')


def view_order_status(request):
    orders = OrderTable.objects.filter(USER_ID__LOGIN_ID_id=request.session['lid']).exclude(status='paid')

    for order in orders:
        order_details = OrderDetails.objects.filter(ORDER_ID=order)
        if order.status != 'paid':
            if all(detail.status == 'accepted' for detail in order_details):
                order.status = 'accepted'
                order.save()

    return render(request, 'User/view_order_status.html', {'orders': orders})


def user_view_more_order_status(request,id):
    order = OrderTable.objects.get(id=id)
    order_details = OrderDetails.objects.filter(ORDER_ID=order)
    total_amount = sum(detail.price for detail in order_details)

    return render(request, 'User/view_more_order_status.html', {
        'order_details': order_details,
        'total_amount': total_amount,
        'order': order
    })


def user_pay_proceed(request, id, amt):
    request.session['rid'] = id
    request.session['pay_amount'] = amt
    client = razorpay.Client(auth=("rzp_test_edrzdb8Gbx5U5M", "XgwjnFvJQNG6cS7Q13aHKDJj"))
    amount_in_paise = int(float(amt) * 100)
    payment = client.order.create({'amount': amount_in_paise, 'currency': "INR", 'payment_capture': '1'})
    return render(request, 'user/UserPayProceed.html',
    {'p': payment, 'val': [], "lid": request.session['lid'], "id": request.session['rid'],"amt":request.session['pay_amount']})


def on_payment_success(request):
    request.session['rid'] = request.GET['id']
    request.session['lid'] = request.GET['lid']
    request.session['amt'] = request.GET['amt']
    ob=OrderTable.objects.get(id=request.session['rid'])
    ob.status='paid'
    ob.amount=request.session['amt']
    ob.save()
    if ob.status == 'paid':
        products = OrderDetails.objects.filter(ORDER_ID=ob)
        for product in products:
            product.PRODUCT_ID.stock -= product.quantity
            product.PRODUCT_ID.save()
    return redirect("/user_order_history")



def user_order_history(request):
    orders = OrderTable.objects.filter(USER_ID__LOGIN_ID=request.session['lid'], status='paid')
    orders_details = []

    for order in orders:
        details = OrderDetails.objects.filter(ORDER_ID=order)
        for detail in details:
            feedback = FeedbackTable.objects.filter(ORDERDETAILS=detail).first()
            print('---++++++-------',feedback)
            orders_details.append({
                'detail': detail,
                'feedback': feedback,
            })
    return render(request, 'User/view_history.html', {'orders_details': orders_details})




def view_rec(request):
    orders = OrderDetails.objects.filter(ORDER_ID__USER_ID__LOGIN_ID=request.session['lid'])
    oids=[]
    for i in orders:
        oids.append(i.PRODUCT_ID.id)
    print("oids",oids)

    oorders=OrderDetails.objects.filter(PRODUCT_ID__id__in=oids)
    ooids=[]
    for i in oorders:

        ooids.append(i.ORDER_ID.USER_ID.id)
    print("ooids",ooids)
    orders1 = OrderDetails.objects.filter(ORDER_ID__USER_ID__id__in=ooids)
    print("orders1",orders1)
    oids1 = []
    for i in orders1:
        if i.PRODUCT_ID.id not in oids:
            oids1.append(i.PRODUCT_ID.id)
    print("oids1",oids1)
    products = ProductTable.objects.filter(id__in=oids1).order_by('-stock')
    plist=[]
    for i in products:
        plist.append(i)
    obh=UserHistoryTable.objects.filter(USER_ID__LOGIN_ID__id=request.session['lid']).order_by('-id')
    print("obh",obh)
    for i in obh:
        products=ProductTable.objects.filter(product_name__icontains=i.Keyword)
        print(products)
        for j in products:
            if j not in plist:
                plist.append(j)
    # return render(request, 'User/view_products.html', {'products': products})

    return render(request, 'User/view_rec.html', {'products': plist})


# def send_review(request, id):
#     product = ProductTable.objects.get(id=id)
#     if request.method == 'POST':
#         user = UserTable.objects.get(id=request.session['lid'])
#         feedback = request.POST['feedback']
#         ratings = request.POST['ratings']
#
#         FeedbackTable.objects.create(
#             PRODUCT_ID=product,
#             USER_ID=user,
#             feedback=feedback,
#             ratings=ratings
#         )
#         return redirect('view_history')  # Redirect to view history after saving
#     return render(request, 'User/view_history.html', {'product': product})


from django.contrib import messages


def submit_review(request):
    if request.method == 'POST':
        order_detail_id = request.POST.get('product_id')  # This should be the OrderDetails ID
        feedback = request.POST.get('feedback')
        rating = request.POST.get('rating')

        if order_detail_id and feedback and rating:
            try:
                # Fetch the specific OrderDetails instance
                order_detail = OrderDetails.objects.get(id=order_detail_id)

                # Create feedback associated with the OrderDetails
                FeedbackTable.objects.create(
                    ORDERDETAILS=order_detail,
                    feedback=feedback,
                    ratings=rating
                )
                messages.success(request, 'Review submitted successfully!')
            except OrderDetails.DoesNotExist:
                messages.error(request, 'Order detail not found.')
        else:
            messages.error(request, 'Please fill all fields.')

    return redirect('/user_order_history')


