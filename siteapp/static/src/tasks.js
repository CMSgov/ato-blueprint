jQuery(document).ready(function ($) {
  $("#cfacts-link").click(function(event) {
    event.preventDefault();
    $("#cfacts-download").submit();
  });
});