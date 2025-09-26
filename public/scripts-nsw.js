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
			gridjs.html(
				`<a href="https://www.nsw.gov.au${item.url?.[0] || '#'}" target="_blank" rel="noopener noreferrer">
					${item.title?.[0] || ""}
				</a>`
			),
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
  const fromValue = document.getElementById("date-from").value;
  const toValue = document.getElementById("date-to").value;

  if (!fromValue && !toValue) {
    renderTable(allData);
    return;
  }

  const fromDate = fromValue ? new Date(fromValue) : null;
  const toDate = toValue ? new Date(toValue) : null;

  const filtered = allData.filter((item) => {
    const dateAdded = new Date(item.added_to_mongo_at);

    if (fromDate && dateAdded < fromDate) return false;
    if (toDate) {
      // add 1 day to include the selected "to" date fully
      const toDateInclusive = new Date(toDate);
      toDateInclusive.setDate(toDateInclusive.getDate() + 1);
      if (dateAdded >= toDateInclusive) return false;
    }

    return true;
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
