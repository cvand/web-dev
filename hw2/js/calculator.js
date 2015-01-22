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
		var screen = document.getElementById("screen-label");
		screen.innerHTML = last_screen;
	} else {
		operation = true;
		last_operation = id;
		
		if (id == 'plus-op') {
		} else if (id == 'minus-op') {

		} else if (id == 'multiply-op') {

		} else if (id == 'divide-op') {

		} else { // equals operation

		}
	}
	return true;
}