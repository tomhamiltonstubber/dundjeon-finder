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

  if ($campaigns_list.length) {
    const update_games_list = () => {
      const form_data = $filter_form.serialize()
      $.get($campaigns_list.data('camps-data-url') + '?' + form_data)
        .done(data => {
          const $games_list_html = games_list.render({games_data: data})
          $campaigns_list.html($games_list_html).show()
        })
        .fail($campaigns_list.html('<div class="error">An error occurred.</div>'))
    }
    update_games_list()
    $('#games-filter-form *').change(() => {
      update_games_list()
    })
  }
}
