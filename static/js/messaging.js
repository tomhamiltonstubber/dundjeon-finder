import $ from 'jquery'
import messages from './templates/messages.njk'

export function render_messages () {
  $.get(window.msg_feed_url + '?c=' + (window.msg_count || 0))
    .done(data => {
      window.msg_count = data.length
      if (data.length) {
        const html = messages.render({'messages': data})
        $('#messages').html(html)
      }
    })
}

export function init_messages () {
  window.msg_count = null
  render_messages()
  setInterval(function () {
    render_messages()
  }, 10000)
}
