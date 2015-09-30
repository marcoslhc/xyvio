var gulpTasks = require('gulp-boilerplate');
var tasks = {
    'css': {
        def: 'gulp-boilerplate-css',
        src: ['./sass/**/*.scss'],
        dest: './dist/css/'
    },
    'clean': {
        def: 'gulp-boilerplate-clean',
        src: ['dist']
    }
};

var gulp = gulpTasks(tasks);

gulp.task('dist', ['clean', 'css']);
