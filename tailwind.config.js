module.exports = {
  purge: {
    enabled: true,
    content: [
      './templates/*.jinja',
      './templates/*/*.jinja',
      './static/js/*.js',
      './static/js/templates/*.njk'
    ]
  },
   darkMode: false, // or 'media' or 'class'
 }  