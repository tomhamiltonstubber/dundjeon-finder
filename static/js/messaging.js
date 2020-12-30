import $ from 'jquery'
import messages from './templates/messages.njk'

export function render_messages (last_id) {
  $.get(window.msg_feed_url + '?last_id=' + (last_id || 0)).done(data => {
    if (data.length) {
      last_id = data[0]['id']
      const html = messages.render({'messages': data})
      $('#messages').html(html)
    }
  })
  return last_id
}

export function init_messages () {
  let last_id = null
  render_messages(last_id)
  setInterval(function () {
    last_id = render_messages(last_id)
  }, 10000)
}
