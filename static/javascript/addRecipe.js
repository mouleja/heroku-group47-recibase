
document.getElementById("source-check").addEventListener("change", function() {

	var sourceName = document.getElementById("sourceName");
	var sourceUrl = document.getElementById("sourceUrl");
	var newSourceName = document.getElementById("newSourceName");
	
	if(this.checked){
		sourceName.classList.remove("no-source");
		if(sourceName.value == 'new_source'){
			newSourceName.classList.remove("no-source");
			sourceUrl.classList.remove("no-source");
			newSourceName.required = true;
		}
		sourceName.required = true;
		sourceName.addEventListener("change", function(){
			if(this.value == 'new_source'){
				newSourceName.classList.remove("no-source");
				sourceUrl.classList.remove("no-source");
				newSourceName.required = true;
			}
			else {
				newSourceName.classList.add("no-source");
				sourceUrl.classList.add("no-source");
				newSourceName.required = false;
			}
		});
	}
	else {
		sourceName.classList.add("no-source");
		sourceUrl.classList.add("no-source");
		newSourceName.classList.add("no-source");
		sourceName.required = false;
		newSourceName.required = false;
	}

});