from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext


# Create your views here.
def index(request):
#     give back initial variable values

    return render(request, 'calculator/calculator.html', {"last_operation": '', "last_screen": '0', "last_result": '0', "operation": 'false'})

def calculate(request):
    try:
        last_result = int(request.REQUEST['last_result'])
    except ValueError:
        last_result = 0
    
    try:
        last_operation = str(request.REQUEST['last_operation'])
    except ValueError:
        last_operation = ''
        
    try:
        last_screen = str(request.REQUEST['last_screen'])
    except ValueError:
        last_screen = '0'
    
    try:
        operation = str(request.REQUEST['operation'])
    except ValueError:
        operation = 'false'
    
    try:
        button = int(request.REQUEST['button'])
    except ValueError:
        button = request.REQUEST['button']
    
    if (last_screen == str('Error')):
        last_screen = '0'
    
    if (isinstance( button, int )):
        if ((last_screen == str('0')) or (operation == str('true'))):
            last_screen = button;
            operation = 'false';
        else:
            last_screen = last_screen + str(button);
    else:
        operation = 'true';
        operand = int(float(last_screen))

        if (last_operation == str('plus-op')):
            last_result = last_result + operand
        elif (last_operation == str('minus-op')):
            last_result = last_result - operand
        elif (last_operation == str('multiply-op')):
            last_result = last_result * operand
        elif (last_operation == str('divide-op')):
            if (operand == 0):
                last_result = 0
                last_operation = ''
                last_screen = 'Error'
                return render(request, 'calculator/calculator.html', {"last_operation": last_operation, "last_screen": last_screen, "last_result": last_result, "operation": operation})
            else:
                last_result = last_result // operand
           
        else:
            last_result = operand
       

        last_screen = str(last_result)
        last_operation = button

        if (button == str('equals-op')):
            last_result = 0
            last_operation = ''
       
    return render(request, 'calculator/calculator.html', {"last_operation": last_operation, "last_screen": last_screen, "last_result": last_result, "operation": operation})
