import { GrantTable } from "./classes/grant-table.js";

//======================================================================================================================
//                                                    Variables
//======================================================================================================================
const grantTableInstances: { [key: string]: GrantTable } = {};
const fromDateInput = document.getElementById("date-from") as HTMLInputElement | null;
const toDateInput = document.getElementById("date-to") as HTMLInputElement | null;
const globalSearch = document.getElementById('global-search') as HTMLInputElement | null;

//======================================================================================================================
//                                                    Functions
//======================================================================================================================
function applyFilter() {
    const fromValue = fromDateInput?.value ?? "";
    const toValue = toDateInput?.value ?? "";
    const fromDate = fromValue ? new Date(fromValue) : null;
    const toDate = toValue ? new Date(toValue) : null;

    // Apply filter to all tables
    for (const key in grantTableInstances) {
        grantTableInstances[key].filterByDate(fromDate, toDate);
    }

    // Clear global search input
    if (globalSearch) {
        globalSearch.value = '';
    }
}

//======================================================================================================================
//                                                    Listeners
//======================================================================================================================
fromDateInput?.addEventListener("change", applyFilter);
toDateInput?.addEventListener("change", applyFilter);

// Table visibility toggles
document.addEventListener('DOMContentLoaded', () => {
    const panel = document.getElementById('filter-panel') as HTMLElement | null;
    const switchesContainer = document.getElementById('filter-switches') as HTMLElement | null;
    if (!panel || !switchesContainer) return;

    const tableDivs = Array.from(document.querySelectorAll('div[id$="-table-container"]')) as HTMLDivElement[];
    const seen = new Set<HTMLElement>();

    tableDivs.forEach((div) => {
        const section = div.closest('section') as HTMLElement | null;
        if (!section) return;
        if (seen.has(section)) return;
        seen.add(section);

        const headingEl = section.querySelector('h2');
        const labelText = headingEl ? (headingEl.textContent || '').trim() : (div.id || 'Section');

        const idSuffix = div.id || Math.random().toString(36).slice(2, 8);
        const checkboxId = 'toggle-' + idSuffix;

        const wrapper = document.createElement('label');
        wrapper.className = 'switch';

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.checked = true;
        checkbox.id = checkboxId;
        checkbox.className = 'switch-input';
        checkbox.setAttribute('aria-label', labelText);

        checkbox.addEventListener('change', () => {
            section.style.display = checkbox.checked ? '' : 'none';
            checkbox.setAttribute('aria-checked', checkbox.checked ? 'true' : 'false');
        });

        const slider = document.createElement('span');
        slider.className = 'slider';

        const labelSpan = document.createElement('span');
        labelSpan.className = 'label-text';
        labelSpan.textContent = labelText;

        wrapper.appendChild(checkbox);
        wrapper.appendChild(slider);
        wrapper.appendChild(labelSpan);
        switchesContainer.appendChild(wrapper);
    });

    const accordionToggle = document.getElementById('filter-accordion-toggle') as HTMLButtonElement | null;
    if (accordionToggle) {
        accordionToggle.addEventListener('click', () => {
            const expanded = accordionToggle.getAttribute('aria-expanded') === 'true';
            accordionToggle.setAttribute('aria-expanded', expanded ? 'false' : 'true');
            if (expanded) {
                panel.hidden = true;
                accordionToggle.textContent = 'Toggle tables ▾';
            } else {
                panel.hidden = false;
                accordionToggle.textContent = 'Toggle tables ▴';
            }
        });
    }

    const selectAllBtn = document.getElementById('select-all') as HTMLButtonElement | null;
    const deselectAllBtn = document.getElementById('deselect-all') as HTMLButtonElement | null;
    const resultsPerPageSelect = document.getElementById('results-per-page') as HTMLSelectElement | null;

    function setAll(checked: boolean) {
        const container = panel as HTMLElement;
        const cbs = Array.from(container.querySelectorAll('input[type="checkbox"]')) as HTMLInputElement[];
        cbs.forEach((cb) => {
            if (cb.checked !== checked) {
                cb.checked = checked;
                cb.dispatchEvent(new Event('change', { bubbles: true }));
            }
        });
    }

    selectAllBtn?.addEventListener('click', () => setAll(true));
    deselectAllBtn?.addEventListener('click', () => setAll(false));
    // Wire results-per-page dropdown: update each GrantTable instance
    if (resultsPerPageSelect) {
        resultsPerPageSelect.addEventListener('change', () => {
            const val = parseInt(resultsPerPageSelect.value, 10) || 10;
            for (const key in grantTableInstances) {
                const inst = grantTableInstances[key];
                // If instance has setPageLimit, call it
                if (typeof (inst as any).setPageLimit === 'function') {
                    (inst as any).setPageLimit(val);
                }
            }
        });
    }
});

// Global search input listener
document.addEventListener('DOMContentLoaded', () => {
    if (globalSearch) {
        globalSearch.addEventListener('input', () => {
            const val = globalSearch.value;
            // Find all gridjs search inputs and set their value
            const gridInputs = document.querySelectorAll<HTMLInputElement>('input.gridjs-input');
            gridInputs.forEach((input) => {
                input.value = val;
                // Trigger input event for each gridjs input
                const event = new Event('input', { bubbles: true });
                input.dispatchEvent(event);
            });
        });
    }
});

//======================================================================================================================
//                                                 Execute on load
//======================================================================================================================
grantTableInstances['bga-grants'] = new GrantTable("bga-grants-table-container", "bga_grants");
grantTableInstances['grant-connect'] = new GrantTable("grant-connect-table-container", "grant_connect");
grantTableInstances['nsw-grants'] = new GrantTable("nsw-grants-table-container", "nsw_grants");
grantTableInstances['vic-grants'] = new GrantTable("vic-grants-table-container", "vic_grants");
grantTableInstances['vic-business'] = new GrantTable("vic-business-table-container", "vic_business");
grantTableInstances['qld-grants'] = new GrantTable("qld-grants-table-container", "qld_grants");
grantTableInstances['qld-advance'] = new GrantTable("qld-advance-grants-table-container", "qld_advance");
grantTableInstances['qld-local'] = new GrantTable("qld-local-grants-table-container", "qld_local");
grantTableInstances['nt-grants'] = new GrantTable("nt-grants-table-container", "nt_grants");
grantTableInstances['nt-business'] = new GrantTable("nt-business-grants-table-container", "nt_business");
grantTableInstances['nt-directory'] = new GrantTable("nt-directory-grants-table-container", "nt_directory");
grantTableInstances['act-grants'] = new GrantTable("act-grants-table-container", "act_grants");
grantTableInstances['wa-grants'] = new GrantTable("wa-grants-table-container", "wa_grants");
grantTableInstances['wa-creative'] = new GrantTable("wa-creative-grants-table-container", "wa_creative");
grantTableInstances['wa-regional'] = new GrantTable("wa-regional-grants-table-container", "wa_regional");
grantTableInstances['tas-grants'] = new GrantTable("tas-grants-table-container", "tas_grants");
grantTableInstances['tas-business'] = new GrantTable("tas-business-table-container", "tas_business");
grantTableInstances['sa-business'] = new GrantTable("sa-business-table-container", "sa_business");
grantTableInstances['sa_human-services'] = new GrantTable("sa-human-services-table-container", "sa_human_services");