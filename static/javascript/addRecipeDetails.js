document.getElementById("ingredient").addEventListener("change", function() {
	console.log(this.value)
	var newIngredient = document.getElementById("new-ingredient");
	var defaultAmount = document.getElementById("default-amount");
	var defaultUnit = document.getElementById("default-unit");
	var calories = document.getElementById("calories");
	if(this.value == 'new_ingredient') {
		newIngredient.required = true;
		newIngredient.classList.remove('no-new-ingredient');
		defaultAmount.classList.remove('no-new-ingredient');
		defaultUnit.classList.remove('no-new-ingredient');
		calories.classList.remove('no-new-ingredient');
	}
	else {
		newIngredient.required = false;
		newIngredient.classList.add('no-new-ingredient');
		defaultAmount.classList.add('no-new-ingredient');
		defaultUnit.classList.add('no-new-ingredient');
		calories.classList.add('no-new-ingredient');
	}

});