from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required

# Import Varification links
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from .forms import RegistrationForm
from .models import Account

from cart.models import Cart, CartItem
from cart.views import _cart_id


# Create your views here.
def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            email = form.cleaned_data["email"]
            phone_number = form.cleaned_data["phone_number"]
            password = form.cleaned_data["password"]

            username = f"{first_name} {last_name}"
            user = Account.objects.create(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
            )
            user.set_password(password)
            user.phone_number = phone_number
            user.save()

            # USER ACTIVATION...
            current_site = get_current_site(request)
            mail_subject = "Please activate your account!"
            message = render_to_string(
                "auth/auth_varification_email.html",
                {
                    "user": user,
                    "domain": current_site,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": default_token_generator.make_token(user),
                },
            )
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            # messages.success(request, 'Thank you for registering with us. We have sent you a verification email to your email address [rathan.kumar@gmail.com]. Please verify it.')
            return redirect("/auth/login/?command=verification&email=" + email)
    else:
        form = RegistrationForm()

    context = {"form": form}

    return render(request, "auth/register.html", context)


def login(request):
    ## ⭐ POST Request Handling:    - Check the user submit the form
    if request.method == "POST":
        ##  ⭐ Get email and password from the formdata.
        email = request.POST["email"]
        password = request.POST["password"]

        ##  ⭐ User Authentication: authenticate user via email and password.
        user = auth.authenticate(request, email=email, password=password)

        ##  ⭐ If User found or authenticated:
        if user is not None:
            ##  ⭐ Merge Anonymous cart with user cart.
            _merge_anonymous_cart_with_user_cart(request, user)

            ##  ⭐  Logs in the user and redirects them (either to checkout or dashboard)
            auth.login(request, user)
            messages.success(request, "You are loggedin now.")

            ## ⭐ Handle redirect to next_page or dashboard
            return _get_redirect_after_login(request)

        ##  ⭐  If User not found then through error.
        else:
            messages.error(request, "Invalid credientials!")
            return redirect("login")

    return render(request, "auth/login.html")


@login_required(login_url="login")
def logout(request):
    auth.logout(request)
    messages.success(request, "you are logged out!")
    return redirect("login")


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Congratulations! Your account is activated.")
        return redirect("login")
    else:
        messages.error(request, "Invalid credientials link.")
        return redirect("register")


@login_required(login_url="login")
def dashboard(request):

    return render(request, "auth/dashboard.html")


def forgotPassword(request):
    if request.method == "POST":
        email = request.POST["email"]
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # USER ACTIVATION...
            current_site = get_current_site(request)
            mail_subject = "Reset your password!"
            message = render_to_string(
                "auth/reset_password_email.html",
                {
                    "user": user,
                    "domain": current_site,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": default_token_generator.make_token(user),
                },
            )
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(
                request, "Password reset email has been sent to your email address."
            )
            return redirect("login")
        else:
            messages.error(request, "Account does not exists.")
            return redirect("forgotPassword")
    else:
        pass
    return render(request, "auth/forgotPassword.html")


def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session["uid"] = uid
        messages.success(request, "Please, reset your password.")
        return redirect("resetPassword")
    else:
        messages.error(request, "This link has been expired.")
        return redirect("login")


def resetPassword(request):
    if request.method == "POST":
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password == confirm_password:
            uid = request.session.get("uid")
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()

            messages.success(request, "Password reset successful.")
            return redirect("login")
        else:
            messages.error(request, "Password does not matched!")
            return redirect("resetPassword")
    else:
        pass
    return render(request, "auth/resetPassword.html")


# --------------------------------------------------------------------------------------------------------------------------------------------#
## ================================================== Helper Methods used in above views ================================================== ##


##  - Helper method to merge anonymous cart with user cart.
def _merge_anonymous_cart_with_user_cart(request, user):
    """
    Merges the anonymous cart items with the authenticated user's cart.
    Handles product variations and quantities intelligently.
    """

    try:
        ##  ⭐  Get the anonymous cart (without user) with session id.
        anonymous_cart = Cart.objects.get(cart_id=_cart_id(request))

        ##  ⭐ Prefetching variations to avoid N+1 queries
        anonymous_items = CartItem.objects.filter(cart=anonymous_cart).prefetch_related(
            "variations"
        )

        if not anonymous_items.exists():
            return

        ##  ⭐ If cart item founds: merge the with the user existing cart.
        if anonymous_items:
            # ✅ Get All cart items of anonymous cart.
            user_items = CartItem.objects.filter(user=user).prefetch_related(
                "variations"
            )
            user_items_map = {}
            #  ✔ Create a lookup directory for user's cart items by variations.
            for item in user_items:
                variations_ids = frozenset(item.variations.values_list("id", flat=True))
                user_items_map[variations_ids] = item

            for anon_item in anonymous_items:
                anon_variation_ids = frozenset(
                    anon_item.variations.values_list("id", flat=True)
                )

                if anon_variation_ids in user_items_map:
                    existing_item = user_items_map[anon_variation_ids]
                    existing_item.quantity += anon_item.quantity
                    existing_item.save()

                    # Delete anonymous cart item.
                    anon_item.delete()
                else:
                    anon_item.user = user
                    anon_item.cart = None
                    anon_item.save()

            anonymous_cart.delete()

    except Cart.DoesNotExist:
        pass
    except Exception as e:
        messages.error(request, f"Error merging cart for user {user.email}: {str(e)}")


##  - Helper method to get redirect after login.
def _get_redirect_after_login(request):
    """
    Dtermines where to redirect the user after login.
    Checks for 'next' parameter in the URL.
    """
    referer_url = request.META.get("HTTP_REFERER")

    if referer_url:
        try:
            # Parse the query string from the referal URL
            from urllib.parse import urlparse, parse_qs

            parse_url = urlparse(referer_url)
            params = parse_qs(parse_url.query)

            if "next" in params:
                next_page = params["next"][0]
                return redirect(next_page)
        except Exception as e:
            messages.warning(request, f"Error parsing redirect URL: {str(e)}")
    return redirect("dashboard")
