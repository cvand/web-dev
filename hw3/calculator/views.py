from django.shortcuts import render

# Create your views here.
def index(request):
#     give back initial variable values

    return render(request, 'calculator/calculator.html', {"last_operation": '', "last_screen": '0', "last_result": '0', "operation": 'false'})

# def calculate(request):
#     int 