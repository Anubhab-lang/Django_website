from django.shortcuts import render, redirect
from django.http import HttpResponse
from main.forms import ProfileForm
from main.models import ChestMl
from .models import Tutorial
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import NewUserForm
import cv2
import matplotlib.image as mpimg
import tensorflow as tf
import matplotlib.pyplot as plt
import scipy.misc


def homepage(request):
    return render(request=request,
                  template_name="main/home.html",
                  context={"tutorials": Tutorial.objects.all})


def register(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"New Account Created: {username}")
            login(request, user)
            messages.info(request, f"You are now logged in as {username}")
            return redirect("main:homepage")
        else:
            for msg in form.error_messages:
                messages.error(request, f"{msg}:{form.error_messages[msg]}")

    form = NewUserForm
    return render(request,
                  "main/register.html",
                  context={"form": form})


def logout_request(request):
    logout(request)
    messages.info(request, "Logged out successfully")
    return redirect("main:homepage")


def chestml_request(request):
    saved = False

    if request.method == "POST":
        # Get the posted form
        MyProfileForm = ProfileForm(request.POST, request.FILES)

        if MyProfileForm.is_valid():
            profile = ChestMl()
            profile.picture = MyProfileForm.cleaned_data["picture"]
            CATEGORIES = ["NORMAL", "PNEUMONIA"]

            def prepare(filepath):
                IMG_SIZE = 60  # 50 in txt-based
                img_array = mpimg.imread(filepath, cv2.IMREAD_GRAYSCALE)  # read in the image, convert to grayscale
                new_array = cv2.resize(img_array, (IMG_SIZE, IMG_SIZE))  # resize image to match model's expected sizing
                plt.imshow(img_array, cmap='binary')
                plt.show()
                return new_array.reshape(-1, IMG_SIZE, IMG_SIZE, 1)  # return the image with shaping that TF wants.

            model = tf.keras.models.load_model("templates/chest-1550435481-0.9902.model")

            prediction = model.predict([prepare(profile.picture)])
            print(prediction)  # will be a list in a list.
            print(CATEGORIES[int(prediction[0][0])])

            profile.save()
            saved = True

        else:
            MyProfileForm = ProfileForm()

    return render(request=request,
                  template_name="main/chestML.html",
                  context={"chest": ChestMl.objects.all})

def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}")
                return redirect("main:homepage")
            else:
                messages.error(request, "Invalid username or password!")
        messages.error(request, "Invalid username or password!")

    form = AuthenticationForm()
    return render(request,
                  "main/login.html",
                  {"form": form})

