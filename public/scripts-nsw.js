let allData = [];

function renderTable(filteredData) {
	const tableDiv = document.getElementById("nsw-grants-table-container");
	tableDiv.innerHTML = ""; // Remove previous table

	  // Store the grid instance globally so we can destroy it
  if (window.gridInstance) {
    window.gridInstance.destroy();
    window.gridInstance = null;
  }

	 window.gridInstance = new gridjs.Grid({
		columns: [
			"Title",
			"Date Added to db",
		],
		data: filteredData.map((item) => [
			item.title?.[0] || "",
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
		renderTable(allData);
		return;
	}
	const filterDate = new Date(dateValue);
	const filtered = allData.filter((item) => {
		// Adjust this if your date field is named differently
		const dateAdded = new Date(item.added_to_mongo_at);
		return dateAdded >= filterDate;
	});
	renderTable(filtered);
});

// Initial fetch and render
fetch('/api/data?collection=nsw_grants')
.then(response => response.json())
.then(data => {
	allData = data;
	renderTable(allData);
});
