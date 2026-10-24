/* Bundle column of the courses table: its cells stay free text (to name a new bundle), with the bundles already entered
   suggested while typing, from a datalist - which DataTable has no option for, hence the list attribute set on its
   input as a Bundle cell gets the focus (on a click, or as soon as it is selected). The browser would suggest the
   bundles containing the typed text: the datalist only holds those starting with it, kept up to date as it is typed.
   Served automatically by Dash from this assets/ folder. */
window.dash_clientside = Object.assign({}, window.dash_clientside, {
    bundles: {
        // The distinct bundles of the table, sorted (kept in the bundle-names store, see layout.py).
        names: function (rows) {
            const names = new Set((rows || []).map(function (row) { return (row.Bundle || "").trim(); })
                                              .filter(function (name) { return name; }));
            window.bundleNames = Array.from(names).sort();
            return window.bundleNames;
        }
    }
});

(function () {
    const BUNDLE_INPUT = "#courses-table td[data-dash-column='Bundle'] input";

    // The datalist of the bundles starting with the given text (whatever the case), created on first use.
    function suggest(text) {
        let datalist = document.getElementById("bundle-options");
        if (!datalist) {
            datalist = document.createElement("datalist");
            datalist.id = "bundle-options";
            document.body.appendChild(datalist);
        }
        const prefix = (text || "").trim().toLowerCase();
        datalist.replaceChildren.apply(datalist, (window.bundleNames || []).filter(function (name) {
            return name.toLowerCase().startsWith(prefix);
        }).map(function (name) {
            const option = document.createElement("option");
            option.value = name;
            return option;
        }));
    }

    document.addEventListener("focusin", function (event) {
        if (event.target.matches(BUNDLE_INPUT)) {
            suggest(event.target.value);
            event.target.setAttribute("list", "bundle-options");
        }
    });
    document.addEventListener("input", function (event) {
        if (event.target.matches(BUNDLE_INPUT))
            suggest(event.target.value);
    });
})();
