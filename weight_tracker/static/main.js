function refreshRecords() {
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
			ul.replaceChildren()
			var li;
			jsonResponse.records.forEach((element) => {
				li = document.createElement("li");
				li.className = "list-group-item";
				li.appendChild(document.createTextNode(element.date));
				li.appendChild(document.createTextNode(" => "));
				li.appendChild(document.createTextNode(element.value));
				ul.appendChild(li);
			});
		});
}

function formSubmit(event) {
	event.preventDefault();
	const body = {
		date: document.querySelector('input[name="date"]').value,
		value: document.querySelector('input[name="value"]').value,
	};
	fetch("/record", {
		method: "POST",
		body: JSON.stringify(body),
		headers: {
			"Content-Type": "application/json",
		},
	})
		.then((_) => refreshRecords())
		.catch((error) => console.log(error));
}

const form = document.getElementById("submitForm");
form.addEventListener("submit", formSubmit);
refreshRecords()
