import { GrantTable } from "./classes/grant-table.js";

//======================================================================================================================
//                                                    Variables
//======================================================================================================================
const grantTableInstances: { [key: string]: GrantTable } = {};

//======================================================================================================================
//                                                    Functions
//======================================================================================================================
function applyFilter() {
    const fromInputId = "date-from";
    const toInputId = "date-to";
    const fromDateInput = document.getElementById(fromInputId) as HTMLInputElement | null;
    const toDateInput = document.getElementById(toInputId) as HTMLInputElement | null;

    const fromValue = fromDateInput?.value ?? "";
    const toValue = toDateInput?.value ?? "";
    const fromDate = fromValue ? new Date(fromValue) : null;
    const toDate = toValue ? new Date(toValue) : null;

    // Apply filter to all tables
    for (const key in grantTableInstances) {
        grantTableInstances[key].filterByDate(fromDate, toDate);
    }
}

//======================================================================================================================
//                                                    Listeners
//======================================================================================================================
const applyFilterBtnEl = document.getElementById("apply-filter");
applyFilterBtnEl?.addEventListener("click", applyFilter);

//======================================================================================================================
//                                                 Execute on load
//======================================================================================================================
grantTableInstances['bga-grants'] = new GrantTable("bga-grants-table-container", "bga_grants");
grantTableInstances['grant-connect'] = new GrantTable("grant-connect-table-container", "grant_connect");
grantTableInstances['nsw-grants'] = new GrantTable("nsw-grants-table-container", "nsw_grants");
grantTableInstances['vic-grants'] = new GrantTable("vic-grants-table-container", "vic_grants");
grantTableInstances['vic-business'] = new GrantTable("vic-business-table-container", "vic_business");
grantTableInstances['qld-grants'] = new GrantTable("qld-grants-table-container", "qld_grants");
grantTableInstances['nt-grants'] = new GrantTable("nt-grants-table-container", "nt_grants");
grantTableInstances['act-grants'] = new GrantTable("act-grants-table-container", "act_grants");
