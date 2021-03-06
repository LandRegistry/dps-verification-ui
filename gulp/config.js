var config = {
  'applicationPath': './verification_ui',
  'sourcePath': './verification_ui/assets/src',
  'destinationPath': './verification_ui/assets/dist',
  'sassPath': 'scss/*.scss',
  'sassIncludePaths': [
    'node_modules'
  ],
  'localhost': 'localhost:8080',
  'nodePath': [
    'node_modules'
  ]
}

if ('NODE_PATH' in process.env) {
  config['nodePath'].push(process.env.NODE_PATH)
  config['sassIncludePaths'].push(process.env.NODE_PATH)
}

module.exports = config
