var last_operation = '';
var last_screen = '0';
var last_result = 0;
var operation = false;

function buttonClicked(element) {
	var id = element.getAttribute('id');
	if (id == null) {
		// the button is a number
		var span = element.childNodes[0].innerHTML;
		var number = parseInt(span);
		if ((last_screen == '0') || operation == true) {
			last_screen = number;
			operation = false;
		}
		else {
			last_screen = last_screen + span;
		}
		showInScreen(last_screen);
	} else {
		operation = true;
		var operand = parseInt(last_screen);
		
		if (last_operation == 'plus-op') {
			last_result = last_result + operand;
		} else if (last_operation == 'minus-op') {
			last_result = last_result - operand;
		} else if (last_operation == 'multiply-op') {
			last_result = last_result * operand;
		} else if (last_operation == 'divide-op') {
			last_result = Math.floor(last_result / operand);
		} else {
			last_result = operand;
		}
		
		if (last_result > 1000000) {
			last_result = 0;
		}
		
		showInScreen(last_result);
		last_operation = id;

		if (id == 'equals-op') {
			last_result = 0;
			last_operation = '';
		}
	}
	return true;
}

function showInScreen(result) {
	var screen = document.getElementById("screen-label");
	screen.innerHTML = result;
	last_screen = result;
}