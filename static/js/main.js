//Validation Script
// Example starter JavaScript for disabling form submissions if there are invalid fields
(function () {
'use strict'

// Fetch all the forms we want to apply custom Bootstrap validation styles to
var forms = document.querySelectorAll('.needs-validation')

// Loop over them and prevent submission
Array.prototype.slice.call(forms).forEach(function (form) {
	form.addEventListener('submit', function (event) {
		if (!form.checkValidity()) {
			event.preventDefault()
			event.stopPropagation()
		}

		form.classList.add('was-validated')
	}, false)
})

})()

// Show / Hide Password
function toggle1(){
	var x = document.getElementById("password1");
	var y = document.getElementById("hide1");
	var z = document.getElementById("hide2");

	if(x.type === 'password') {
		x.type = 'text';
		y.style.display = "block";
		z.style.display = "none";
	}

	else {
		x.type = 'password';
		y.style.display = "none";
		z.style.display = "block";
	}
}

function toggle2(){
	var x = document.getElementById("password2");
	var y = document.getElementById("hide1");
	var z = document.getElementById("hide2");

	if(x.type === 'password') {
		x.type = 'text';
		y.style.display = "block";
		z.style.display = "none";
	}

	else {
		x.type = 'password';
		y.style.display = "none";
		z.style.display = "block";
	}
}


$("#myuploadfile").bind('change', function(){
	var filename = $("#myuploadfile").val();

	const  fileType =this.files[0].type;
	const validImageTypes = ['image/jpeg', 'image/jpg', 'image/png'];

	if (!validImageTypes.includes(fileType)) {
		document.getElementById("myuploadfile").value = null;
	}
})

//declearing html elements

const imgDiv = document.querySelector('.newprofilepic');
const img = document.querySelector('#newphoto');
const file = document.querySelector('#myuploadfile');
const uploadBtn = document.querySelector('#myuploadBtn');

//if user hover on img div 

imgDiv.addEventListener('mouseenter', function(){
	uploadBtn.style.display = "block";
});

//if we hover out from img div

imgDiv.addEventListener('mouseleave', function(){
	uploadBtn.style.display = "none";
});

//lets work for image showing functionality when we choose an image to upload

//when we choose a foto to upload

file.addEventListener('change', function(){
	//this refers to file
	const choosedFile = this.files[0];

	const  fileType =this.files[0].type;
	const validImageTypes = ['image/jpeg', 'image/jpg', 'image/png'];

	if (validImageTypes.includes(fileType)) {
		const reader = new FileReader(); //FileReader is a predefined function of JS

		reader.addEventListener('load', function(){
			img.setAttribute('src', reader.result);
		});
		reader.readAsDataURL(choosedFile);		
	}
	else{
		document.getElementById("myuploadfile").value = null;
	}
});