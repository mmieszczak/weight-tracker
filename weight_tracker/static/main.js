const myHeading = document.querySelector("h1");
myHeading.textContent = "Hello world!";
fetch("/records")
  .then(
    (response) => {
      if (response.ok) return response.json();
      else throw new Error("Failed");
    },
    (networkError) => {
      console.log(networkError.message);
    }
  )
  .then((jsonResponse) => {
		var ul = document.getElementById("myList");
		var li;
		jsonResponse.records.forEach((element) => {
			li = document.createElement("li");
			li.className = "list-group-item";
			li.appendChild(document.createTextNode(element.date));
			li.appendChild(document.createTextNode(" => "));
			li.appendChild(document.createTextNode(element.value));
			ul.appendChild(li);
		})
  });
