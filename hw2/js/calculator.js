var last_operation = '';
var last_screen = '0';
var last_result = 0;
var operation = false;

function prepareListeners() {
	var elements = document.getElementsByTagName('button');

	for (var i = 0; i < elements.length; i++) {
		elements[i].addEventListener("click", function() {
			buttonClicked(this);
		});
	}
}

function buttonClicked(element) {
	var id = element.getAttribute('id');
	if (id == null) {
		// the button is a number
		var span = element.childNodes[0].innerHTML;
		var number = parseInt(span);
		if ((last_screen == '0') || operation == true) {
			last_screen = number;
			operation = false;
		} else {
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
			if (operand == 0) {
				reset();
				showInScreen('Error');
				last_screen = '0';
				return true;
			} else {
				last_result = Math.floor(last_result / operand);
			}
		} else {
			last_result = operand;
		}

		showInScreen(last_result);
		last_screen = last_result;
		last_operation = id;

		if (id == 'equals-op') {
			reset();
		}
	}
	return true;
}

function reset() {
	last_result = 0;
	last_operation = '';
}

function showInScreen(result) {
	var screen = document.getElementById("screen-label");
	screen.innerHTML = result;
}