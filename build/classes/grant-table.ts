import { Grid, html } from "gridjs";

export class GrantTable {
	private tableContainerId: string;
	private mongoDbCollection: string;
	private allData: any[] = [];
	private grid: Grid | null = null;

	constructor(
		tableContainerId: string,
		mongoDbCollection: string,
		allData: any = [],
	) {
		this.allData = allData;
		this.tableContainerId = tableContainerId;
		this.mongoDbCollection = mongoDbCollection;

		// Fetch data and render on page load
		this.fetchData();
	}

	private async fetchData() {
		try {
			const response = await fetch(
				`/api/data?collection=${this.mongoDbCollection}`
			);
			this.allData = await response.json();
			this.renderTable(this.allData);
		} catch (error) {
			console.error("Error fetching data:", error);
		}
	}

private renderTable(data: any[]) {
	const tableContainerEl = document.getElementById(this.tableContainerId);
	if (!tableContainerEl) return;

	tableContainerEl.innerHTML = ""; // Clear existing content

	// Destroy existing grid if present
	if (this.grid) {
		this.grid.destroy();
		this.grid = null;
	}

	// Create new grid
	this.grid = new Grid({
		columns: ["Title", "Date Added to db"],
		data: data.map((item) => [
			html(
				`<a href="${item.link || "#"}" target="_blank" rel="noopener noreferrer">
					${item.title || ""}
				</a>`
			),
			item.added_to_mongo_at
				? new Date(item.added_to_mongo_at).toLocaleDateString("en-GB")
				: "",
		]),
		search: true,
		pagination: true,
		sort: true,
	});

	this.grid.render(tableContainerEl);
}

	public filterByDate(fromDate: Date | null, toDate: Date | null) {
		if (!fromDate && !toDate) {
			this.renderTable(this.allData);
			return;
		}

		const filtered = this.allData.filter((item) => {
			const dateAdded = new Date(item.added_to_mongo_at);

			if (fromDate && dateAdded < fromDate) return false;

			if (toDate) {
				// include full "to" date
				const toDateInclusive = new Date(toDate);
				toDateInclusive.setDate(toDateInclusive.getDate() + 1);
				if (dateAdded >= toDateInclusive) return false;
			}

			return true;
		});

		this.renderTable(filtered);
	}
}
