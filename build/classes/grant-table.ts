import { Grid, html } from "gridjs";

export class GrantTable {
	private tableContainerId: string;
	private mongoDbCollection: string;
	private allData: any[] = [];
	private grid: Grid | null = null;

	constructor(
		tableContainerId: string,
		mongoDbCollection: string,
		allData: any = []
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
			columns: ["Title", "Link", "Date Added to db"],
			data: data.map((item) => [
				item.title,
				html(
					`<a href="${
						item.link || "#"
					}" target="_blank" rel="noopener noreferrer">
					Link
				</a>`
				),
				item.added_to_mongo_at
					? new Date(item.added_to_mongo_at).toLocaleDateString("en-AU")
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

		let fromDateNoTime: Date | null = null;
		let toDateNoTime: Date | null = null;
		if (fromDate) {
			fromDateNoTime = new Date(fromDate);
			fromDateNoTime.setHours(0, 0, 0, 0);
		}
		if (toDate) {
			toDateNoTime = new Date(toDate);
			toDateNoTime.setHours(23, 59, 59, 999);
		}

		const filtered = this.allData.filter((item) => {
			// Convert UTC date from Mongo to AEST
			const aestDateString = new Date(
				item.added_to_mongo_at
			).toLocaleDateString("en", { timeZone: "Australia/Sydney" });
			const aestDate = new Date(aestDateString);

			// Check if date falls within the range
			if (fromDateNoTime && toDateNoTime) {
				return aestDate >= fromDateNoTime && aestDate <= toDateNoTime;
			} else if (fromDateNoTime) {
				return aestDate >= fromDateNoTime;
			} else if (toDateNoTime) {
				return aestDate <= toDateNoTime;
			}
			return true;
		});

		this.renderTable(filtered);
	}
}
