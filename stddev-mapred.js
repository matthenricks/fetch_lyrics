// derived from http://en.wikipedia.org/wiki/Algorithms_for_calculating_variance#Parallel_algorithm
// Source: https://gist.github.com/RedBeard0531/1886960

function map() {
    emit(this.wordid, // Or put a GROUP BY key here
         {sum: this.year * this.count, // the field you want stats for
          min: this.year * this.count,
          max: this.year * this.count,
          count: this.count,
          diff: 0, // M2,n:  sum((val-mean)^2)
    });
}

function reduce(key, values) {
    var a = values[0]; // will reduce into here
    for (var i=1/*!*/; i < values.length; i++){
        var b = values[i]; // will merge 'b' into 'a'


        // temp helpers
        var delta = a.sum/a.count - b.sum/b.count; // a.mean - b.mean
        var weight = (a.count * b.count)/(a.count + b.count);
        
        // do the reducing
        a.diff += b.diff + delta*delta*weight;
        a.sum += b.sum;
        a.count += b.count;
        a.min = Math.min(a.min, b.min);
        a.max = Math.max(a.max, b.max);
    }

    return a;
}

function finalize(key, value){ 
    value.avg = value.sum / value.count;
    value.variance = value.diff / value.count;
    value.stddev = Math.sqrt(value.variance);
    return value;
}
