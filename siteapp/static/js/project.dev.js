"use strict";

jQuery(document).ready(function ($) {
  $('#state_change').select2();
  $('#type_change').select2();
  var project_invitation_info = JSON.parse(document.getElementById('send_invitation').textContent);
  var implemented = 0;
  $('li.usa-sidenav__item a').each(function () {
    if ($(this).data('status') === 'implemented') {
      ++implemented;
    }
  });
  $('.usa-step-indicator__current-step').text(implemented);
  $('#control-next').click(function (event) {
    event.preventDefault();
    var form = $('#narrative-form'),
        next_url = $(this).attr('href');
    $.ajax({
      url: '/controls/smt/_save/',
      method: 'POST',
      data: form.serialize()
    }).done(function (data) {
      window.location = next_url;
    });
  });
  $('#control-save').click(function (event) {
    event.preventDefault();
    var form = $('#narrative-form');
    $.ajax({
      url: '/controls/smt/_save/',
      method: 'POST',
      data: form.serialize()
    }).done(function (data) {
      window.location.reload();
    });
  });
  $('#control-delete').click(function (event) {
    event.preventDefault(); // Confirm deletion

    var result = confirm('Delete statement?');

    if (result) {
      var form = $('#narrative-form'),
          next_url = $('#control-next').attr('href');

      if (!next_url) {
        var controls = $('#system_id').val(),
            components = $('#producer_element_id').val();
        next_url = '/controls/' + controls + '/component/' + components;
      }

      $.ajax({
        url: '/controls/smt/_delete/',
        method: 'POST',
        data: form.serialize()
      }).done(function (data) {
        window.location = next_url;
      });
    }
  });
  $('#project-invite').click(function (event) {
    event.preventDefault();
    var info = project_invitation_info;
    show_invite_modal('Invite To Project Team (' + info.model_title + ')', 'Invite a colleague to join this project team.', info, 'Please join the project team for ' + info.model_title + '.', {
      project: info.model_id,
      add_to_team: '1'
    }, function () {
      window.location.reload();
    });
    return false;
  });
  $('.add-control').click(function (event) {
    event.preventDefault();
    var form_id = $(this).data('family'),
        values = {};
    $('#' + form_id + ' :input').each(function (index) {
      var input = $(this);

      if (input.attr('name') !== 'sid') {
        values[input.attr('name')] = input.val();
      }
    });
    $('#' + form_id + ' :checkbox:checked').each(function (index) {
      values['sid'] = $(this).val();
      $.ajax({
        url: '/controls/smt/_save/',
        method: 'POST',
        data: values
      });
    });
    window.location.reload();
  });
});

function show_import_project_modal(id, callback) {
  var m = $('#import_project_modal');
  $('#import_loading_spinner').hide();
  m.modal();
}

function fillJSONContent(file) {
  var aid = JSON.parse(document.getElementById('auto_id').textContent);
  filecontents = $("#".concat(aid)).prop('files')[0];
  var reader = new FileReader();
  reader.readAsText(filecontents);

  reader.onload = function (e) {
    $("#{aid}").val(e.target.result);
  };
}