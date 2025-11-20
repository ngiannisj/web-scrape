import { Grid, html } from "gridjs";

export class GrantTable {
	private tableContainerId: string;
	private mongoDbCollection: string;
	private allData: any[] = [];
	private currentViewData: any[] = [];
	private grid: Grid | null = null;
	private pageLimit: number = 10;

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
			// Keep track of what's currently rendered (initially all data)
			this.currentViewData = this.allData;
			this.renderTable(this.allData);
		} catch (error) {
			console.error("Error fetching data:", error);
		}
	}

	private renderTable(data: any[]) {
		const tableContainerEl = document.getElementById(this.tableContainerId);
		if (!tableContainerEl) return;

		tableContainerEl.innerHTML = ""; // Clear existing content

		// Update current view data (used for CSV export)
		this.currentViewData = data;

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
			search: {
				selector: (cell, rowIndex, cellIndex) => {
				// ✅ return string always
				return cellIndex === 0 ? String(cell) : "";
				}
			},
			pagination: {
				limit: this.pageLimit,
			},
			sort: true,
		});

		this.grid.render(tableContainerEl);

		this.updateCsvDownloadButton();
	}

	/**
	 * Update the page limit (rows per page) and re-render the table with current view data.
	 */
	public setPageLimit(limit: number) {
		this.pageLimit = limit;
		// Re-render with the currently viewed data so pagination takes effect
		this.renderTable(this.currentViewData);
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

		this.currentViewData = filtered;
		this.renderTable(filtered);
	}

	private updateCsvDownloadButton() {
		// Remove any existing download button for this container
		const buttonContainerId = `${this.tableContainerId}-button`;
		const buttonContainerEl = document.getElementById(buttonContainerId);
		const existingBtn = buttonContainerEl?.querySelector('.csv-download-btn');
		if (existingBtn) existingBtn.remove();

		// Create download CSV button
		const downloadBtn = document.createElement('button');
		downloadBtn.className = 'csv-download-btn';
		downloadBtn.type = 'button';
		downloadBtn.textContent = 'Download CSV';
		downloadBtn.addEventListener('click', () => {
			try {
				const csv = this.convertToCsv(this.currentViewData);
				const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
				const url = URL.createObjectURL(blob);
				const a = document.createElement('a');
				a.href = url;
				a.download = `${this.mongoDbCollection || 'data'}.csv`;
				document.body.appendChild(a);
				a.click();
				a.remove();
				URL.revokeObjectURL(url);
			} catch (err) {
				console.error('Failed to generate CSV:', err);
			}
		});

		// Insert the button before the table content
		buttonContainerEl?.appendChild(downloadBtn);
	}

	/**
	 * Convert the provided data array into a CSV string.
	 * Exports the same columns shown in the grid: Title, Link, Date Added to db
	 */
	private convertToCsv(data: any[]): string {
		const header = ["Title", "Link", "Date Added to db"];
		const rows = data.map((item) => {
			const title = item.title ?? "";
			const link = item.link ?? "";
			const date = item.added_to_mongo_at
				? new Date(item.added_to_mongo_at).toLocaleString("en-AU", { timeZone: "Australia/Sydney" })
				: "";
			return [title, link, date];
		});

		const escape = (v: any) => this.escapeCsvCell(v);

		const csvLines = [header.map(escape).join(","), ...rows.map((r) => r.map(escape).join(","))];
		return csvLines.join("\r\n");
	}

	private escapeCsvCell(value: any): string {
		if (value === null || value === undefined) return '""';
		const s = String(value).replace(/"/g, '""');
		return `"${s}"`;
	}
}
