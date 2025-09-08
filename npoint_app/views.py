from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import HttpResponse
from .models import UserProfile, JSONData, PasswordResetCode
from .forms import SignUpForm, JsonDataForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.db.models import F, Q, Sum
import json
from django.core.paginator import Paginator
import random
from .mail import send_mail
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.urls import reverse
from django.conf import settings
from rest_framework.authtoken.models import Token
from django.views.decorators.http import require_POST

# Create your views here.

def humanize_number(value):
    """Format numbers as 1.2K, 3.4M, etc."""
    if value is None:
        return "0"
    if value >= 1_000_000:
        return f"{value/1_000_000:.1f}M".rstrip("0").rstrip(".")
    if value >= 1_000:
        return f"{value/1_000:.1f}K".rstrip("0").rstrip(".")
    return str(value)

def site_stats(request):
    total_users = UserProfile.objects.count()
    total_jsons = JSONData.objects.count()
    total_api_calls = JSONData.objects.aggregate(total=Sum("access_count"))["total"] or 0

    return {
        "total_users": humanize_number(total_users),
        "total_jsons": humanize_number(total_jsons),
        "total_api_calls": humanize_number(total_api_calls),
    }

def login_page(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)

            # "Remember me" (if unchecked, expire at browser close)
            if not request.POST.get("remember_me"):
                request.session.set_expiry(0)

            return redirect("main")
        else:
            messages.error(request, "Invalid username/password.")
    else:
        form = AuthenticationForm(request)

    return render(request, "npoint_app/login.html", {"form": form})   

def register_page(request):
    if request.method == "POST":
        reg_form = SignUpForm(request.POST)
        if reg_form.is_valid():
            user = reg_form.save()       # password hashed, user saved
            auth_login(request, user)    # log them in
            return redirect("my_account")
        messages.error(request, "Please correct the errors below.")
    else:
        reg_form = SignUpForm()

    # also pass a login form for the other pane and open the register tab on errors
    return render(request, "npoint_app/register.html", {
        "form": AuthenticationForm(request),
        "reg_form": reg_form,
        "active_tab": "register",
    })

def logout_page(request):
    auth_logout(request)
    return redirect("home")

def home(request):
    if request.user.is_authenticated:
        q = (request.GET.get("q") or "").strip()
        obj = JSONData.objects.filter(is_public=True).order_by('-created_at')
        if q:
            obj = obj.filter(Q(title__icontains=q) | Q(description__icontains=q))
        
        paginator = Paginator(obj, 12)
        json_files = paginator.get_page(request.GET.get('page'))
        # json_files = paginator.get_page(page_number)
        params = request.GET.copy()
        params.pop("page", None)
        querystring = params.urlencode()
        
        return render(request, 'npoint_app/main.html', {"json_files": json_files, "q": q,
            "querystring": querystring,})
    else:
        return render(request, 'npoint_app/index.html')

def base(request):  
        
        return render(request, 'npoint_app/base.html')

@login_required(login_url='login')
def my_account(request):
    # always have a token (masked)
    token, _ = Token.objects.get_or_create(user=request.user)
    masked = f"{token.key[:4]}••••••••••••••••••••••••{token.key[-4:]}"

    # show-once full token: pop it so it disappears after first render
    latest = request.session.pop("latest_api_token", None)

    # if request.method == "GET":
    #     if not request.user.is_authenticated:
    #         return redirect("login")
    #     user = UserProfile.objects.get(username=request.user.username)
    #     return render(request, 'npoint_app/myaccount.html', {"user": user, "ctx":ctx})

    if request.method == "POST":
        user = request.user
        action = request.POST.get("action")
        if action == "profile":
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            username = request.POST.get("username")
            email = request.POST.get("email")
            profile_picture = request.FILES.get("profile_picture")

            # Update user fields
            user.first_name = first_name
            user.last_name = last_name
            user.username = username
            user.email = email
            pic = profile_picture
            if pic:
                if not str(pic.content_type).startswith("image/"):
                    messages.error(request, "Please upload an image file.")
                    return redirect("my_account")
                if pic.size > 1 * 1024 * 1024:  # 1MB
                    messages.error(request, "Image must be 1MB or smaller.")
                    return redirect("my_account")
                # Optional: delete old file to avoid orphaned media
                old = getattr(user, "profile_picture", None)
                user.profile_picture = pic
                # Save first so new file is stored
                user.save()
                if old and old.name and old != user.profile_picture:
                    try:
                        old.delete(save=False)
                    except Exception:
                        pass
            else:
                user.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("my_account")
        
        elif action == "delete":
            user.delete()
            messages.success(request, "Your account has been deleted.")
            return redirect("login")
    

    return render(request, 'npoint_app/myaccount.html', {"user": request.user, "api_token_masked": masked,
        "latest_api_token": latest,})

@login_required(login_url='login')
@require_POST
def regenerate_token(request):
    Token.objects.filter(user=request.user).delete()
    token = Token.objects.create(user=request.user)
    messages.success(request, "A new API token has been generated. Copy it now.")
    request.session["latest_api_token"] = token.key  # will be shown once
    return redirect("my_account")

@login_required(login_url='login')
def main(request):
    q = (request.GET.get("q") or "").strip()
    obj = JSONData.objects.filter(is_public=True).order_by('-created_at')
    if q:
        obj = obj.filter(Q(title__icontains=q) | Q(description__icontains=q))
    
    paginator = Paginator(obj, 12)
    json_files = paginator.get_page(request.GET.get('page'))
    # json_files = paginator.get_page(page_number)
    params = request.GET.copy()
    params.pop("page", None)
    querystring = params.urlencode()
    
    return render(request, 'npoint_app/main.html', {"json_files": json_files, "q": q,
        "querystring": querystring })


def json_viewer(request, username, title_slug, json_id):
    obj = JSONData.objects.filter(pk=json_id).first()
    
    data = obj.json_content if obj else "{}"
    # increment access_count on GET
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except Exception:
            # fall back; or show an error
            pass
    pretty_json = json.dumps(data, indent=2, ensure_ascii=False)

    if request.method == "GET":
        JSONData.objects.filter(pk=obj.pk).update(access_count=F('access_count') + 1)
        obj.refresh_from_db(fields=["access_count"])

    return render(request, "npoint_app/json_viewer.html", {"json": obj, "pretty_json": pretty_json,})




@login_required(login_url='login')
def json_form(request):
    if request.method == "POST":
        form = JsonDataForm(request.POST, request.FILES)
        
        if form.is_valid():
            
            json_data = form.save(commit=False)
            if json_data.json_picture:
                # pic = json_data.json_picture
                # if not str(pic.content_type).startswith("image/"):
                pic = request.FILES.get("json_picture")
                if not str(pic.content_type).startswith("image/"):
                    messages.error(request, "Please upload an image file.")
                    return render(request, 'npoint_app/json_form.html', {"form": form})
                if pic.size > 1 * 1024 * 1024:  # 1MB
                    messages.error(request, "Image must be 1MB or smaller.")
                    return render(request, 'npoint_app/json_form.html', {"form": form})
            
            
            json_data.user = request.user
            json_data.save()
            content_url = request.build_absolute_uri(
                reverse("public-json-content", kwargs={"username":request.user.username, "slug":json_data.slug, "json_id": json_data.pk})
            )
            json_data.json_api = content_url
            json_data.save()
            messages.success(request, "JSON data saved successfully.")
            return render(request, "npoint_app/json_form.html", {"form": form, "json_data": json_data})
        else:
            
            messages.error(request, "Please correct the errors below.")
            return render(request, 'npoint_app/json_form.html', {"form": form})
    else:
        form = JsonDataForm()
        return render(request, 'npoint_app/json_form.html', {"form": form})
            
    return render(request, 'npoint_app/json_form.html')

@login_required(login_url='login')
def my_json_form(request):
    q = (request.GET.get("q") or "").strip()
    obj = JSONData.objects.filter(user=request.user).order_by('-created_at')
    if q:
        obj = obj.filter(Q(title__icontains=q) | Q(description__icontains=q))
    
    
    paginator = Paginator(obj, 12)
    json_forms = paginator.get_page(request.GET.get('page'))
    user = request.user

    params = request.GET.copy()
    params.pop("page", None)
    querystring = params.urlencode()
    if request.method == "GET":
        return render(request, 'npoint_app/my_json_forms.html', {"json_forms": json_forms, "user": user, "q": q,
            "querystring": querystring })
    
    return render(request, 'npoint_app/my_json_forms.html')

@login_required(login_url='login')
def edit_json_form(request, title_slug, json_id):
    obj = get_object_or_404(JSONData, pk=json_id, user=request.user)
    
    if request.method == "POST":
        form = JsonDataForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            json_data = form.save(commit=False)
            
            
            if 'json_picture' in request.FILES:
                pic = request.FILES.get("json_picture")
                if not str(pic.content_type).startswith("image/"):
                    messages.error(request, "Please upload an image file.")
                    return render(request, 'npoint_app/edit_json_form.html', {"form": form, "json_data": obj})
                if pic.size > 1 * 1024 * 1024:  # 1MB
                    messages.error(request, "Image must be 1MB or smaller.")
                    return render(request, 'npoint_app/edit_json_form.html', {"form": form, "json_data": obj})
                old = getattr(obj, "json_picture", None)
                json_data.json_picture = pic
                json_data.save()
                if old and old.name and old != json_data.json_picture:
                    try:
                        old.delete(save=False)
                    except Exception:
                        pass
            else:
                json_data.save()
            json_data.save()
            content_url = request.build_absolute_uri(
                reverse("public-json-content", kwargs={"username":request.user.username, "slug":json_data.slug, "json_id": json_data.pk})
            )
            
            json_data.json_api = content_url
            json_data.save()
            pretty_json = json.dumps(obj.json_content, indent=2, ensure_ascii=False)
            messages.success(request, "JSON data updated successfully.")
            return render(request, "npoint_app/edit_json_form.html", {"form":form, "json_data":obj, "pretty_json": pretty_json})
        else:
            pretty_json = json.dumps(obj.json_content, indent=2, ensure_ascii=False)
            messages.error(request, "Please correct the errors below.")
            return render(request, 'npoint_app/edit_json_form.html', {"form": form, "json_data": obj, "pretty_json": pretty_json})
    else:
        form = JsonDataForm(instance=obj)
        pretty_json = json.dumps(obj.json_content, indent=2, ensure_ascii=False)
        return render(request, 'npoint_app/edit_json_form.html', {"form": form, "json_data": obj, "pretty_json": pretty_json})

@login_required(login_url='login')
def delete_json_form(request, json_id):
    obj = get_object_or_404(JSONData, pk=json_id, user=request.user)

    # keep a handle to the file before deleting the row
    old_file = obj.json_picture

    obj.delete()  # remove DB row

    # remove file from storage (if any)
    if old_file and old_file.name:
        try:
            old_file.storage.delete(old_file.name)
        except Exception:
            pass

    messages.success(request, "JSON data deleted successfully.")
    return redirect("my_json_form")

def docs(request):
    return render(request, 'npoint_app/docs.html')

def privacy_policy(request):
    return render(request, 'npoint_app/privacy_policy.html')
def terms_of_service(request):
    return render(request, 'npoint_app/terms_of_service.html')
def handler404(request):
    return render(request, 'npoint_app/404.html', status=404)

def password_setting(request):
    # Decide which account
    reset_user_id = request.session.get("reset_user_id")
    if reset_user_id:
        target_user = get_object_or_404(UserProfile, pk=reset_user_id)
        mode = "reset"
    elif request.user.is_authenticated:
        target_user = request.user
        mode = "change"
    else:
        messages.error(request, "Start a password reset first.")
        return redirect("password_reset")

    if request.method == "POST":
        new_pw = request.POST.get("new_password", "")
        confirm_pw = request.POST.get("confirm_password", "")

        if not new_pw or not confirm_pw:
            messages.error(request, "Please fill in all password fields.")
            return redirect("password_setting")
        if new_pw != confirm_pw:
            messages.error(request, "Passwords do not match.")
            return redirect("password_setting")

        # Optional: if mode == "change", verify current password here

        # Validate strength
        try:
            validate_password(new_pw, user=target_user)
        except ValidationError as e:
            for err in e.messages:
                messages.error(request, err)
            return redirect("password_setting")

        # Hash + save
        target_user.set_password(new_pw)
        target_user.save(update_fields=["password"])

        if mode == "change":
            # keep user logged in after change
            update_session_auth_hash(request, target_user)
            messages.success(request, "Password updated successfully.")
            return redirect("my_account")

        # mode == "reset"
        PasswordResetCode.objects.filter(user=target_user, is_used=False).update(is_used=True)
        request.session.pop("reset_user_id", None)
        messages.success(request, "Password has been reset. Please sign in.")
        return redirect("login")

    return render(request, "npoint_app/reset_password.html", {"mode": mode})

def password_reset_request(request):
    if request.method == "POST":
        step = request.POST.get("step")

        if step == "request":
            
            obj = get_object_or_404(UserProfile, username=request.POST.get("username"))
            if obj:
                email = obj.email
                # Generate a reset code (in a real app, use a secure method)
                reset_code = str(random.randint(100000, 999999))
                # Save the reset code to the user's profile or a separate model (not implemented here)
                # Send the reset code via email
                pass_code = PasswordResetCode.objects.filter(user=obj).first()
                if pass_code:
                    pass_code.reset_code = reset_code
                    pass_code.is_used = False
                    pass_code.save()
                else:
                    PasswordResetCode.objects.create(user=obj, reset_code=reset_code)
                send_mail(receiver_email=email, reset_code=reset_code)

                messages.success(request, "A password reset code has been sent to your email.")
                return render(request, "npoint_app/password_reset.html", {"stage": "confirm", "pass_code": pass_code})
            else:
                messages.error(request, "User does not exist.")
                return redirect("password_reset")
            
        elif step == "confirm":
            reset_code = request.POST.get("reset_code")
            obj = get_object_or_404(PasswordResetCode, reset_code=reset_code, is_used=False)
            if obj:
                request.session["reset_user_id"] = obj.user.pk   # obj is your PasswordResetCode
                return redirect("password_setting")
        
    
    return render(request, 'npoint_app/password_reset.html', {"stage": "request", "pass_code": None})
