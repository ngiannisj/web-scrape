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
		gridjs.html(
			`<a href="${item["link"] || '#'}" target="_blank" rel="noopener noreferrer">
				${item["title"] || ""}
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
	document.querySelector(".media_gif__MBeQG").style.display = "block";
  const fromValue = document.getElementById("date-from").value;
  const toValue = document.getElementById("date-to").value;

  if (!fromValue && !toValue) {
    renderTableConnect(allDataConnect);
    return;
  }

  const fromDate = fromValue ? new Date(fromValue) : null;
  const toDate = toValue ? new Date(toValue) : null;

  const filtered = allDataConnect.filter((item) => {
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

  renderTableConnect(filtered);
});

// Initial fetch and render
fetch('/api/data?collection=grant_connect')
.then(response => response.json())
.then(data => {
	allDataConnect = data;
	renderTableConnect(allDataConnect);
});
