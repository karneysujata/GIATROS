from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm, SearchForm, appointmentForm
from django.contrib.auth.decorators import login_required
from .models import Profile, dummyDoctor, Doctor, appointment, User
from django.contrib import messages
from django.core.files import File
import googlemaps
import json
from geopy import geocoders
import names
import random
from random import randint
from six import string_types

insurances = ["Aetna", "American Republic", "Amerigroup", "Bakery & Confectionary Union Plan", "CareSource", "Cigna",
              "Commercial Insurance Company", "Community Health Choice", "Coventry Health Care", "Golden Rule",
              "Government Employees Health Association", "Health Net", "HealthPlus", "HealthPlus Amerigroup", "Medico",
              "Midwest Health Plan", "National Elevator", "Principal Life", "UnitedHealthCare", "Universal American",
              "Blue Cross and Blue Shield"]

specialities = ["Opthalmologist", "Dermatologist", "Cardiologist", "Psychiatrist", "Gastroenterologist", "ENT", "Obstetrician", "Neurologist",
                "Dentist", "Prosthodontist", "Endodontist", "Implantologist", "Ayurveda","Acupuncturist", "Physiotherapist",
                "Psychologist", "Audiologist", "Speech Therapist", "Dietitian", "General"]

def whoAmI(current_user):
    haveProfile = Profile.objects.all().filter(user=current_user)
    if haveProfile.exists():
        print("It is None")
        return False
    return True



def user_login(request):
    if request.method == 'POST':
        form =  LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'],password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return render(request, 'account/dashboard.html', {'form':form,'amIdoc':whoAmI(request.user)})
            else:
                return HttpResponse('Disabled account')
        else:
            return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form':form})

@login_required
def dashboard(request):
    return render(request,'account/dashboard.html',{'section': 'dashboard'})

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            # Set the chosen password
            new_user.set_password(
                    user_form.cleaned_data['password'])
            # Save the User object
            new_user.save()
            profile = Profile.objects.create(user=new_user)
            return render(request,
                    'account/register_done.html',
                    {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request,'account/register.html',{'user_form': user_form})

@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user,data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile,
                       data=request.POST,
                       files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
    else:
        messages.success(request, 'Error updating your profile')
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(
        instance=request.user.profile)
    return render(request,
                  'account/edit.html',
                  {'user_form': user_form,
                  'profile_form': profile_form})



def delete_appointment(request,pk):
    print("The received id:",pk)
    print("trying to get here")
    print("Deleting:",appointment.objects.all().filter(doc=Doctor.objects.all().filter(id_num=pk))[0].delete())
    return render(request,'account/myAppointments.html',{'my_appointments': appointment.objects.all().filter(patient = Profile.objects.all().filter(user=request.user)[0])})

def my_apps(request):
    return render(request,'account/myAppointments.html',{'my_appointments': appointment.objects.all().filter(patient = Profile.objects.all().filter(user=request.user)[0])})

def my_doc_apps(request):
    testing = appointment.objects.all().filter(doc = Doctor.objects.all().filter(user=request.user)[0])
    return render(request,'account/docAppointments.html',{'my_appointments': appointment.objects.all().filter(doc = Doctor.objects.all().filter(user=request.user)[0]),'amIdoc':whoAmI(request.user)})


def phn():
    n = '0000000000'
    while '9' in n[3:6] or n[3:6]=='000' or n[6]==n[7]==n[8]==n[9]:
        n = str(random.randint(10**9, 10**10-1))
    return n[:3] + '-' + n[3:6] + '-' + n[6:]

def isSpeciality(theFilter):
    if (theFilter in specialities):
        return True
    else:
        return False

def isInsurance(theFilter):
    if (theFilter in insurances):
        return True
    else:
        return False

def index(request):
    search_form = SearchForm(auto_id=False)
    if request.method == 'POST':
        search_form =  SearchForm(request.POST)
        if search_form.is_valid():
            inputAddress = search_form.cleaned_data['search']#Search Term
            theFilter = search_form.cleaned_data['attribute']#Search Term
            if (inputAddress == "3031 S 70th St, Omaha"):
                return render(request, 'account/index.html',{'search_form': search_form,'doctors': Doctor.objects.all()})
            else:
                hPlace = 'hospital'
                # Geocoding an address
                gmaps = googlemaps.Client(key='AIzaSyAYCiTaPolA8Y-JbDjXTmfpjuJ-FaJAR8Q')
                # Derive lat and long of a given Place
                g = geocoders.GoogleV3(api_key='AIzaSyAYCiTaPolA8Y-JbDjXTmfpjuJ-FaJAR8Q')
                derived = g.geocode(inputAddress, timeout=10)
                derLocation = []
                derLocation.append(derived.latitude)
                derLocation.append(derived.longitude)
                print("Before Here!!!")
                if (isinstance(theFilter, (int, float))):
                    print("After Here!!!")
                    result = gmaps.places_nearby(derLocation, radius=theFilter, type=hPlace)
                else:
                    result = gmaps.places_nearby(derLocation, radius=1500, type=hPlace)
                j = json.loads(json.dumps(result))
                jsonData = j["results"]
                doctors = []
                for item in jsonData:
                    fullname = names.get_full_name()
                    name = item.get("name")#organization
                    speciality = random.choice(specialities)
                    ins = random.choice(insurances)
                    vicinity = item.get("vicinity")#address
                    rtng = random.randint(0, 5)
                    phone_number = phn()
                    num = random.randint(1, 300)
                    valid = True
                    try:
                        int(theFilter)
                    except ValueError:
                        print("I am false")
                        valid = False
                    if (isSpeciality(theFilter) and speciality == theFilter):
                        doctors.append(dummyDoctor(fullname = fullname, organization = name,specialization = speciality,insurance = ins,rating = rtng, phoneNumber = phone_number,address = vicinity, digit = num ))
                    if (isInsurance(theFilter) and ins == theFilter):
                        doctors.append(dummyDoctor(fullname = fullname, organization = name,specialization = speciality,insurance = ins,rating = rtng, phoneNumber = phone_number,address = vicinity, digit = num))
                    if (valid):
                        if(isinstance(int(theFilter), (int, float))):
                             doctors.append(dummyDoctor(fullname = fullname, organization = name,specialization = speciality,insurance = ins,rating = rtng, phoneNumber = phone_number,address = vicinity, digit = num))
                return render(request, 'account/index.html',{'search_form': search_form,'doctors': doctors,})
    return render(request,'account/index.html',{'search_form': search_form})

def about(request):
    return render(request,'account/about.html')


@login_required
def make_appointment(request, pk):
    appointment_form =appointmentForm()
    search_form = SearchForm(auto_id=False)
    if request.method == "POST":
        form = appointmentForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['scheduled_date']#Search Term
            time = form.cleaned_data['scheduled_time']#Search Term
            app = appointment(patient = Profile.objects.all().filter(user=request.user)[0], doc = Doctor.objects.all().filter(id_num=pk)[0], scheduled_date = date, scheduled_time = time, status = 'Upcoming')
            app.save()
            return render(request,'account/index.html',{'search_form': search_form})
    else:
        print("The filtered result is:",Doctor.objects.all().filter(id_num=pk))
    return render(request,'account/makeAppointment.html',{'doctor':Doctor.objects.all().filter(id_num=pk)[0],'appointment_form': appointment_form})
