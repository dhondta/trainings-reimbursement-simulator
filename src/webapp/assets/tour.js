/* Guided tour of the dashboard, with Driver.js (see instance.py): started with the tour button of the navbar, which a
   hint points to on a user's first session (see the tour-auto store in layout.py). Some steps show the dashboard's
   controls at work (the departure date, the cap mode, the switches of the rendement periods' chart) by setting them as
   the user would, and everything is set back as it was once the tour ends. Served automatically by Dash from this
   assets/ folder. */
window.dash_clientside = Object.assign({}, window.dash_clientside, {
    tour: {
        // Starts the tour on a click of the tour button only (not when the language changes the texts, after a first
        //  click), and points to that button on a first session, once the page has had time to render.
        request: function (auto, nClicks, texts) {
            const context = window.dash_clientside.callback_context;
            const triggered = context.triggered.map(function (t) { return t.prop_id; });
            if (nClicks && triggered.includes("tour-btn.n_clicks")) {
                // The hint is dismissed by the click on the button it points to.
                if (window.tourHint && window.tourHint.isActive()) {
                    window.tourHint.destroy();
                    window.dash_clientside.set_props("tour-finished", {data: Date.now()});
                }
                return Date.now();
            }
            if (auto && texts && !window.tourHintShown) {
                window.tourHintShown = true;
                setTimeout(function () { window.dash_clientside.tour.hint(texts); }, 1500);
            }
            return window.dash_clientside.no_update;
        },

        // The hint of a first session: the tour button only, until it is clicked or the hint is closed - either way,
        //  it is not shown again to this user (see mark_tour_done).
        hint: function (texts) {
            if (!window.driver || (window.tourDriver && window.tourDriver.isActive()))
                return;
            window.tourHint = window.driver.js.driver({
                popoverClass: "tour-popover",
                showButtons: ["close"],
                steps: [{element: "#tour-btn", popover: {description: texts.hint, side: "bottom", align: "end"}}],
                onDestroyStarted: function () {
                    window.dash_clientside.set_props("tour-finished", {data: Date.now()});
                    window.tourHint.destroy();
                },
            });
            window.tourHint.drive();
        },

        start: function (run, texts, slider, range, capMode, fullSchedule, unbundled, unbundledDisabled) {
            const noUpdate = window.dash_clientside.no_update;
            if (!run || !texts || !window.driver || (window.tourDriver && window.tourDriver.isActive()))
                return noUpdate;
            const setProps = window.dash_clientside.set_props;
            // Each step sets the controls it shows, from the state they were in when the tour started: going back and
            //  forth through the steps thus always shows the same thing.
            const original = {slider: slider, cap: capMode, full: !!fullSchedule, unbundled: !!unbundled};
            let applied = Object.assign({}, original);
            function apply(state) {
                const wanted = Object.assign({}, original, state || {});
                if (wanted.slider !== applied.slider)
                    setProps("departure-slider", {value: wanted.slider});
                if (wanted.cap !== applied.cap)
                    setProps("cap-mode-select", {value: wanted.cap});
                if (wanted.full !== applied.full)
                    setProps("full-schedule-switch", {value: wanted.full});
                if (wanted.unbundled !== applied.unbundled)
                    setProps("unbundled-switch", {value: wanted.unbundled});
                applied = wanted;
            }
            // {date} and {total} in a step's text: the departure date and the total to reimburse, as displayed, kept up
            //  to date as the charts follow the controls set by the step.
            const sources = {
                date: function () { return document.getElementById("departure-date-label"); },
                total: function () { return document.querySelector("#total-reimbursement-card .text-primary"); },
            };
            function describe(text) {
                return text.replace(/\{(date|total)\}/g, '<strong class="tour-live" data-source="$1"></strong>');
            }
            function refresh() {
                document.querySelectorAll(".tour-live").forEach(function (span) {
                    const source = sources[span.dataset.source]();
                    span.textContent = source ? source.textContent : "";
                });
            }
            const timer = setInterval(refresh, 250);
            function step(key, element, state) {
                const [title, description] = texts.steps[key];
                return {element: element, popover: {title: title, description: describe(description)},
                        onHighlightStarted: function () { apply(state); }};
            }
            const [first, last] = range || [slider, slider];
            const middle = Math.round((first + last) / 2);
            window.tourDriver = window.driver.js.driver({
                showProgress: true,
                smoothScroll: true,
                popoverClass: "tour-popover",
                progressText: texts.progress,
                nextBtnText: texts.next,
                prevBtnText: texts.prev,
                doneBtnText: texts.done,
                onPopoverRender: refresh,
                steps: [
                    step("rules", "#law-summary-card"),
                    step("preset", "#preset-dropdown"),
                    step("import", "#browse-btn"),
                    step("export", "#export-btn"),
                    step("pdf", "#export-pdf-btn"),
                    step("add_row", "#add-row-btn"),
                    step("slider_start", "#departure-card", {slider: first}),
                    step("slider_middle", "#departure-card", {slider: middle}),
                    step("slider_end", "#departure-card", {slider: last}),
                    step("cap_bunch", "#cap-mode-group", {cap: "bunch"}),
                    step("cap_period", "#cap-mode-group", {cap: "period"}),
                    step("bar", "#reimbursement-bar-card"),
                    step("figures", "#metric-cards"),
                    step("timeline", "#rendement-timeline"),
                    step("full_schedule", "#timeline-card", {full: true}),
                    // The comparison with the courses not bundled is only available with a bundle.
                    unbundledDisabled ? step("unbundled_none", "#timeline-card")
                                      : step("unbundled", "#timeline-card", {unbundled: true}),
                    step("explanation", "#law-application"),
                ],
                // However the user ends it (done, closed, or escaped), even before its first step is shown.
                onDestroyStarted: function () {
                    clearInterval(timer);
                    apply();
                    setProps("tour-finished", {data: Date.now()});
                    window.tourDriver.destroy();
                },
            });
            window.tourDriver.drive();
            return noUpdate;
        },
    },
});
