let allDataConnect = [];

function renderTableConnect(filteredData) {
	const tableDiv = document.getElementById("grant-connect-table-container");
	tableDiv.innerHTML = ""; // Remove previous table

	  // Store the grid instance globally so we can destroy it
  if (window.gridInstanceConnect) {
    window.gridInstanceConnect.destroy();
    window.gridInstanceConnect = null;
  }

	window.gridInstanceConnect = new gridjs.Grid({
		columns: [
			"Title",
			"Date Added to db",
		],
		data: filteredData.map((item) => [
			item["title"] || "",
			item.added_to_mongo_at
				? new Date(item.added_to_mongo_at).toLocaleDateString("en-GB")
				: "",
		]),
		search: true,
		pagination: true,
		sort: true,
	}).render(tableDiv);
}

// Filter logic
document.getElementById("apply-filter").addEventListener("click", function () {
	const dateValue = document.getElementById("date-filter").value;
	if (!dateValue) {
		renderTableConnect(allDataConnect);
		return;
	}
	const filterDate = new Date(dateValue);
	const filtered = allDataConnect.filter((item) => {
		// Adjust this if your date field is named differently
		const dateAdded = new Date(item.added_to_mongo_at);
		return dateAdded >= filterDate;
	});
	renderTableConnect(filtered);
});

// Initial fetch and render
fetch('/api/data?collection=grant_connect')
.then(response => response.json())
.then(data => {
	allDataConnect = data;
	renderTableConnect(allDataConnect);
});
