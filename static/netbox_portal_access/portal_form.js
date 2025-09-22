(function () {
  function onReady(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  }

  onReady(function () {
    var typeSel = document.getElementById("id_vendor_ct");
    var vendorSel = document.getElementById("id_vendor");
    if (!typeSel || !vendorSel) return;

    var providerCT = vendorSel.dataset.providerCt || "";
    var tenantCT = vendorSel.dataset.tenantCt || "";

    function rewire() {
      var ct = typeSel.value;

      if (!ct) {
        vendorSel.setAttribute("disabled", "disabled");
        // clear any previous selection
        if (window.jQuery) { jQuery(vendorSel).val(null).trigger("change"); }
        return;
      }

      vendorSel.removeAttribute("disabled");

      var url = "";
      if (ct === providerCT) {
        url = "/api/circuits/providers/";
      } else if (ct === tenantCT) {
        url = "/api/tenancy/tenants/";
      }

      if (url) {
        // APISelect reads the data-url attribute when fetching options
        vendorSel.setAttribute("data-url", url);
        // clear the current selection so the user can pick from the new source
        if (window.jQuery) { jQuery(vendorSel).val(null).trigger("change"); }
      }
    }

    // initial state + respond to changes
    rewire();
    typeSel.addEventListener("change", rewire);
  });
})();

