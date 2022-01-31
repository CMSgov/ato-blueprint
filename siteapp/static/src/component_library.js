jQuery(document).ready(function($) {
  var val = $( "#type_project_change" ).val();
  if (! val ) {
      $("#project_submit_id").prop('disabled', true);
  }
  var keyword = $('#searchbox').val(),
      staticUrl = window.location.href.split('?')[0],
      delimiter = ',';
  $('#keyword').val(keyword);

  $('#library-search').submit(function(event) {
    event.preventDefault();
    $('#keyword').val($('#searchbox').val());
    $('#library-filters').trigger('change');
  });

  $('#library-filters').change(function() {
    var queryString = $(this).serialize().replace(/(?<=([^\?\&\=]+=)([^\&\=]+))(\&\1)/g, delimiter);
    var url = !queryString ? staticUrl : staticUrl + '?' + queryString;
    window.location.replace(url);
  })

  $( "#type_project_change" ).change(function (e) {
      var disabled = $("#type_project_change option:selected").prop('disabled');
      var value = e.target.value;
      if (!value) {
          disabled = true;
      }
      $("#project_submit_id").prop('disabled', disabled);
  });
});