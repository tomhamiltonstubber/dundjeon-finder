import $ from 'jquery'
import conf_modal from '../js/templates/conf_modal.njk'

export function confirm_modal (title, text, $form) {
  if ($('#df-modal').length) {
    $('#df-modal').remove()
  }
  const modal = conf_modal.render({'text': text, 'title': title})
  $('body').append(modal)
  const $modal = $('#df-modal')
  $modal.find('.close').click(() => {
    $modal.hide()
  })
  $modal.find('.confirm').click(() => {
    $form.submit()
  })
}
