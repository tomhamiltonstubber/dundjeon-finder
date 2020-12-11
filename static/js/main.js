import $ from 'jquery'
import '../scss/main.scss'
import games_list from '../js/templates/games_list.njk'

window.$ = window.jQuery = $

$(document).ready(() => {
  init_games_list()
})

const init_games_list = () => {
  const $filter_form = $('#filter_form')
  const $games_list = $('#campaigns-list')

  if ($games_list.length) {
    const update_games_list = () => {
      const form_data = $filter_form.serialize()
      $.get($games_list.data('camps-data-url') + '?' + form_data)
        .done(data => {
          const $games_list_html = games_list.render({games_data: data})
          $games_list.html($games_list_html).show()
        })
        .fail($games_list.html('<div class="error">An error occurred.</div>'))
    }
    update_games_list()
    $('#games_list_filter_field').change(() => {
      update_games_list()
    })
  }
}
