var gulpTasks = require('gulp-boilerplate');
var tasks = {
    'css': {
        def: 'gulp-boilerplate-css',
        src: ['./less'],
        dest: 'dist/css/main.css'
    },
    'clean': {
        def: 'gulp-boilerplate-clean',
        src: ['dist']
    }
};

var gulp = gulpTasks(tasks);
