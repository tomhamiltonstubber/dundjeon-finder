import $ from 'jquery'
import '../scss/main.scss'
import "tailwindcss/tailwind.css"
import games_list from '../js/templates/games_list.njk'

window.$ = window.jQuery = $

$(document).ready(() => {
  init_games_list()
  menu()
})

const menu = () => {
  const $menu_toggle = $('#nav-toggle');
  const $side_menu = $('#side-menu');

  $($menu_toggle).click(() => {
    if($($menu_toggle).hasClass("active")){
      $($menu_toggle).removeClass("active");
      $($side_menu).removeClass("active");
    }else{
      $($menu_toggle).addClass("active");
      $($side_menu).addClass("active");
    }
  });
}

const init_games_list = () => {
  const $filter_form = $('#filter_form')
  const $campaigns_list = $('#campaigns-list')
  const $loading_screen = $('#campaigns-loading-screen')

  if ($campaigns_list.length) {
    const update_games_list = () => {
      const form_data = $filter_form.serialize()
      $.get($campaigns_list.data('camps-data-url') + '?' + form_data)
        .done(data => {
          const $games_list_html = games_list.render({games_data: data})
          $campaigns_list.html($games_list_html).show()
          setTimeout(function(){
            $loading_screen.removeClass("active");
          }, 500)
        })
    }
    update_games_list()
    $('#games-filter-form input, #games-filter-form select').on("change", function(event) {
      $loading_screen.addClass("active");
      update_games_list()
    })
  }
}

$(".alert").on("click", function(){
  $(this).fadeOut();
  setTimeout(function(){
      $(this).remove();
  }, 3000)
});

$(".theme-option").on("click", function(){
  var $theme = $(this).data("theme");

  // Remove previous theme class from body and add new
  $("body").removeClass (function (index, css) {
    return (css.match (/(^|\s)theme-\S+/g) || []).join(' ');
  });
  $("body").addClass($theme);

  // Add selected to new theme option and remove from previous
  $(".theme-option.selected").removeClass("selected");
  $(this).addClass("selected");
});


$('[data-method="POST"]').not('[data-confirm]').not('.no-submit').click(function (e) {
  const $a = $(this)
  const link = $a.attr('href')
  e.preventDefault()
  if (link === '#') {
    return
  }
  const form = $('#post-form')
  form.attr('action', link)
  for (const [key, value] of Object.entries($a.data())) {
    if (key !== 'method') {
      $('<input>').attr({type: 'hidden', name: key, value: value}).appendTo(form)
    }
  }
  form.submit()
})
